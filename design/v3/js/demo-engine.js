/* 데모 변환 엔진 — 백엔드 연결 전 임시 구현.
   실제 MODES(src/hwp2md/web/static/app.js)와 같은 인터페이스를 지킨다:
     convert(file) -> Promise<{status, body}>   body 는 /api/convert 응답과 같은 모양
     zip(file)     -> Promise<Blob>             실패 시 .code 를 가진 Error
   백엔드에 연결할 때는 이 파일 대신 실제 MODES 를 넣으면 된다. */
(function () {
  "use strict";

  const MAX_INPUT_BYTES = 52428800;
  const STATUS = { empty: 400, too_large: 413, not_hwp: 415, unsupported: 415, convert_failed: 422 };
  const MESSAGE = {
    empty: "빈 파일입니다",
    too_large: "파일이 너무 큽니다",
    not_hwp: "not an HWP 5.0 or HWPX file: <memory>",
    unsupported: "encrypted document: <memory>",
    convert_failed: "truncated record at offset 120",
  };

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  let forcedError = null; // 데모 도크의 "오류 보기"가 한 번 쓰는 값

  function errorBody(code) {
    return { status: STATUS[code], body: { error: { code: code, message: MESSAGE[code] } } };
  }

  function check(file) {
    if (forcedError) { const c = forcedError; forcedError = null; return c; }
    if (file && file.size === 0) return "empty";
    if (file && file.size > MAX_INPUT_BYTES) return "too_large";
    return null;
  }

  async function convert(file, latency) {
    await wait(latency);
    const code = check(file);
    if (code) return errorBody(code);
    return { status: 200, body: JSON.parse(JSON.stringify(window.HWP2MD_DEMO_PAYLOAD)) };
  }

  /* ---------- 아주 작은 zip 작성기 (무압축 STORE, UTF-8 파일명) ---------- */
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(bytes) {
    let c = 0xffffffff;
    for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  }

  function buildZip(entries) {
    const enc = new TextEncoder();
    const parts = [];
    const central = [];
    let offset = 0;
    const DOS_DATE = (0 << 9) | (1 << 5) | 1; // 1980-01-01, 서버 build_zip 과 같은 고정 시각
    entries.forEach(({ name, data }) => {
      const nameBytes = enc.encode(name);
      const crc = crc32(data);
      const local = new DataView(new ArrayBuffer(30));
      local.setUint32(0, 0x04034b50, true);
      local.setUint16(4, 20, true);
      local.setUint16(6, 0x0800, true); // UTF-8 파일명
      local.setUint16(8, 0, true);
      local.setUint16(10, 0, true);
      local.setUint16(12, DOS_DATE, true);
      local.setUint32(14, crc, true);
      local.setUint32(18, data.length, true);
      local.setUint32(22, data.length, true);
      local.setUint16(26, nameBytes.length, true);
      local.setUint16(28, 0, true);
      parts.push(new Uint8Array(local.buffer), nameBytes, data);

      const cen = new DataView(new ArrayBuffer(46));
      cen.setUint32(0, 0x02014b50, true);
      cen.setUint16(4, 20, true);
      cen.setUint16(6, 20, true);
      cen.setUint16(8, 0x0800, true);
      cen.setUint16(10, 0, true);
      cen.setUint16(12, 0, true);
      cen.setUint16(14, DOS_DATE, true);
      cen.setUint32(16, crc, true);
      cen.setUint32(20, data.length, true);
      cen.setUint32(24, data.length, true);
      cen.setUint16(28, nameBytes.length, true);
      cen.setUint32(42, offset, true);
      central.push(new Uint8Array(cen.buffer), nameBytes);
      offset += 30 + nameBytes.length + data.length;
    });
    const cenSize = central.reduce((s, p) => s + p.length, 0);
    const end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true);
    end.setUint16(8, entries.length, true);
    end.setUint16(10, entries.length, true);
    end.setUint32(12, cenSize, true);
    end.setUint32(16, offset, true);
    return new Blob([...parts, ...central, new Uint8Array(end.buffer)], { type: "application/zip" });
  }

  function base64ToBytes(b64) {
    const bin = atob(b64);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  // 응답의 preview_markdown 안 data URI 를 이미지 파일 바이트로 되돌린다 (링크 등장 순서로 대응)
  function imagesFromPayload(p) {
    const dir = p.image_dir.replace(/ /g, "%20");
    const names = [...p.markdown.matchAll(/\]\(([^)]+)\)/g)].map((m) => m[1]).filter((h) => h.startsWith(dir + "/"));
    const datas = [...p.preview_markdown.matchAll(/\]\(data:[^;]+;base64,([^)]+)\)/g)].map((m) => m[1]);
    const out = new Map();
    names.forEach((href, i) => {
      const file = href.slice(dir.length + 1);
      if (!out.has(file) && datas[i]) out.set(file, base64ToBytes(datas[i]));
    });
    return out;
  }

  async function zip(file, latency) {
    const res = await convert(file, latency);
    if (res.body.error) {
      const err = new Error(res.body.error.message);
      err.code = res.body.error.code;
      throw err;
    }
    const p = res.body;
    const entries = [{ name: p.name + ".md", data: new TextEncoder().encode(p.markdown) }];
    imagesFromPayload(p).forEach((data, file) => entries.push({ name: p.image_dir + "/" + file, data: data }));
    return buildZip(entries);
  }

  /* ---------- 브라우저 모드 준비 흉내 (실제는 Pyodide 로드 약 1분) ---------- */
  let loaded = false;
  let loading = null;
  function load() {
    if (loaded) return Promise.resolve();
    if (!loading) loading = wait(1600).then(() => { loaded = true; });
    return loading;
  }

  window.Hwp2mdDemo = {
    MODES: {
      server: {
        convert: (file) => convert(file, 750),
        zip: (file) => zip(file, 350),
      },
      browser: {
        async convert(file) { await load(); return convert(file, 450); },
        async zip(file) { await load(); return zip(file, 200); },
      },
    },
    loadBrowser: load,
    forceError(code) { forcedError = code || "not_hwp"; },
    sampleFile() {
      return new File([new Uint8Array(24576)], "2026_가상_공고문.hwpx", { type: "application/octet-stream" });
    },
  };
})();
