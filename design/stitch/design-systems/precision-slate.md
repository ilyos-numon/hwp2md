## Brand & Style

This design system defines an ultra-focused, developer-grade document conversion utility engineered for converting Korean word processor files (HWP / HWPX) to clean, standard Markdown. The interface prioritizes density, structural clarity, and zero cognitive friction. 

Inspired by productivity tools like Linear and Raycast, the style operates on strict minimalism and purposeful utility. It completely rejects marketing-oriented fluff, gratuitous gradients, and heavy skeuomorphic drop shadows. Instead, it relies on crisp 1px structural borders, deliberate typographic hierarchy, and deterministic visual states. The emotional resonance is calm, hyper-efficient, and trustworthy—delivering immediate certainty that complex formatting, tables, and nested structures will parse flawlessly.

## Layout & Spacing

The layout is structured around an adaptive split-pane workstation designed to maximize functional density without visual clutter:

- **Canvas Constraints:** A locked utility viewport for the main application view with an optional fluid max-width container (`1440px`) centered on ultra-wide screens.
- **Split Conversion Grid (Desktop & Tablet Landscape):** A balanced dual-column view (50/50 split) separated by a 1px vertical divider with an interactive resizer handle. The left pane manages drag-and-drop ingestion and HWP outline navigation; the right pane renders synchronized Markdown code alongside live rendered HTML previews.
- **Reflow Architecture (Mobile & Tablet Portrait):** Converts the dual-column layout into a segmented tabbed interface (`Source`, `Markdown`, `Preview`), keeping the action bar docked to the bottom thumb zone.
- **Rhythm & Grid Alignment:** All spacing follows a compact 4px baseline module (`0.25rem`). Component paddings remain tight (`0.5rem` to `0.75rem`) to maximize visible document real estate.

## Elevation & Depth

This design system avoids blurred atmospheric shadows and skeuomorphic drop-offs. Visual separation and layering are achieved strictly through **low-contrast outlines** and **tonal background stepping**:

- **Level 0 (Canvas Base):** Light mode `#FAFAFA`, dark mode `#0B0F17`. Serves as the bedrock workspace behind utility cards.
- **Level 1 (Panels & Surfaces):** Light mode `#FFFFFF`, dark mode `#111827`. Enclosed in a 1px solid border (`#E5E7EB` light / `#1F2937` dark). Used for the document parser frame, conversion workbench, and toolbars.
- **Level 2 (Dropdowns, Popovers, Overlays):** Elevated surfaces share Level 1 tonal fills but employ a crisp perimeter stroke (`#D1D5DB` light / `#374151` dark) paired with a tight, non-diffuse utility shadow: `0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)` (light mode) or `0 4px 12px rgba(0, 0, 0, 0.4)` (dark mode).
- **Focus Rings:** Distinct 2px solid rings offset by 2px (`#2563EB` light / `#3B82F6` dark) replace generic focus blurs to ensure accessible keyboard navigation.

## Components

### Buttons
- **Primary Action (Convert / Download):** Solid fill (`#2563EB` light / `#3B82F6` dark), white text, 6px border radius, height `36px`, padding `0 14px`. Hover initiates a 1-step tone shift (`#1D4ED8` light / `#2563EB` dark) with `100ms ease` transition.
- **Secondary / Ghost (Copy, Clear, Settings):** Transparent background with a 1px border (`#E5E7EB` light / `#1F2937` dark). On hover: `#F3F4F6` (light) / `#1F2937` (dark).
- **Icon Buttons (Format toggles, Sync scroll):** Square `32px × 32px`, 6px corner radius, unbordered until hovered.

### File Drop Zone (Ingestion Area)
- Centered empty-state zone framed by a 1px dashed border (`#D1D5DB` light / `#374151` dark).
- Drag-over state shifts border to 1px solid `#2563EB` with a 4% accent background tint.
- Includes a dedicated file chip indicator showing filename, `.hwp` or `.hwpx` badge, file weight, and immediate conversion status icon.

### Form Inputs & Toggles
- **Inputs:** Height `36px`, 1px solid border (`#D1D5DB` light / `#374151` dark), background `#FFFFFF` (light) / `#111827` (dark). Focus state triggers a crisp blue outline without layout shift.
- **Checkboxes & Radios:** `16px × 16px` with a 4px corner radius for checkboxes. Checked state displays solid `#2563EB` with an inset white micro-check.
- **Conversion Option Switches (MathJax toggle, Image extraction):** Compact `16px` track height with an internal sliding indicator dot.

### Code & Document Previews
- **Split Workspace:** Dual viewport featuring sticky utility headers showing character count, read time, and export options.
- **Markdown Raw Pane:** Line numbers aligned to the left in muted text (`#64748B` light / `#9CA3AF` dark) separated by a subtle 1px vertical track. JetBrains Mono font rendered at `0.8125rem` with `1.375rem` line height.
- **Copy Drawer / Quick Notification:** High-contrast floating pill badge (`#0F172A` in light, `#F9FAFB` in dark with inverse text) appearing bottom-center for exactly 1500ms when code is copied.

### Status Chips & Badges
- **Format Badges:** Font size `0.6875rem`, monospace weight 500, padding `2px 6px`. HWP uses a subtle blue tint, HWPX uses an emerald tint, and Markdown output uses an amber or slate tint.
- **Processing Indicators:** A non-intrusive 2px linear progress bar pinned directly beneath the active file card rather than a blocking modal overlay.