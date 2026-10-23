## Brand & Style

This design system delivers a professional, welcoming, and high-efficiency utility experience tailored for Korean productivity workflows. Translating legacy HWP/HWPX documents into structured Markdown requires immediate trust, mechanical precision, and low cognitive friction. 

The aesthetic is modern, restrained minimalism with friendly utility cues:
- **Clean & Systematic**: Content and file preview take priority over decorative elements.
- **Welcoming & Human**: Soft sky tints, approachable curvature, and accessible contrast soften the technical complexity of file parsing.
- **Reliable Craft**: Crisp micro-borders, purposeful elevation, and instant tactile feedback reflect speed and data fidelity.

## Layout & Spacing

Layouts follow a fluid, responsive container model anchored to an 8px base rhythm with 4px sub-increments for compact utility controls.

### Screen Adaptations
- **Mobile (< 768px)**: Single column flow. File upload surfaces stack vertically above the preview pane. Margins are fixed at `1rem` (`space-md`). Touch targets maintain a minimum dimension of 44x44px.
- **Tablet (768px - 1023px)**: Flexible workspace layout. Dual column orientation allowed when batch conversion lists are populated. Margins set to `1.5rem`.
- **Desktop (≥ 1024px)**: Dual-pane split workbench (Source HWP metadata/upload on the left, interactive split-pane Markdown editor and rendered preview on the right). Max container width is clamped at `1440px` with centered auto-margins.

### Spatial Rhythm
- Use `space-xs` (4px) and `space-sm` (8px) for badge gaps, inline icons, and button inner padding.
- Use `space-md` (16px) for form control stacking, standard card padding, and chip arrays.
- Use `space-lg` (24px) to `space-xl` (32px) for segment breaks, drop zone perimeter paddings, and section headers.

## Elevation & Depth

Visual hierarchy uses flat structural containment backed by soft ambient diffusion, preventing visual clutter in multi-column translation views.

### Hierarchy Tiers
- **Level 0 (Flat / Canvas)**: Page background (`#F6F9FF` light, `#111827` dark). No shadow.
- **Level 1 (Structural Surfaces)**: Main converter panels, preview panes, and standard toolbars.
  - Border: `1px solid #E0E8F4` (Dark: `#334155`).
  - Shadow (Light): `0 1px 3px 0 rgba(23, 43, 77, 0.04), 0 1px 2px -1px rgba(23, 43, 77, 0.02)`.
  - Shadow (Dark): `0 1px 3px 0 rgba(0, 0, 0, 0.3)`.
- **Level 2 (Interactive Cards & File Drops)**: Resting upload drop zones, conversion status cards, and hovered list rows.
  - Border: `1px solid #E0E8F4` (Dark: `#334155`).
  - Shadow (Light): `0 4px 6px -1px rgba(23, 43, 77, 0.05), 0 2px 4px -2px rgba(23, 43, 77, 0.03)`.
- **Level 3 (Overlays & Active Drag States)**: Active file drag-and-drop overlays, modal dialogs, and floating copy notifications.
  - Border: `1px solid #276EF1` with light theme diffuse glow.
  - Shadow (Light): `0 12px 24px -4px rgba(39, 110, 241, 0.12), 0 4px 6px -2px rgba(23, 43, 77, 0.04)`.
  - Shadow (Dark): `0 12px 24px -4px rgba(0, 0, 0, 0.5)`.

## Components

### Buttons
- **Primary (Convert / Download)**: Solid `#276EF1` background with white text. Hover transitions to `#1E5ED8`. Height is 40px (desktop) or 48px (touch). Radius is 8px.
- **Secondary (Copy / Clear)**: Background `#EEF4FF` with `#276EF1` text. In dark mode, `#202F4A` background with `#81ADFF` text. Hover adds 1px solid border.
- **Ghost (Preview Toggles)**: Transparent background, `#64748B` text, shifting to soft accent background on hover.

### File Drop Zone (Core Component)
- Resting state: 2px dashed `#E0E8F4` border, `#FFFFFF` background, 12px radius, centered upload icon and dual-language helper text.
- Drag active state: 2px solid `#276EF1` border, `#E9F2FF` background, subtle 4px blur scale-in animation.

### Chips & Extension Badges
- Compact pill tokens.
- HWP/HWPX badge: Deep slate background with crisp white typography.
- Markdown (.md) badge: `#E9F2FF` fill with `#276EF1` bold typography.
- Status chips: Animated spinner with label for active jobs; green soft fill for success.

### Inputs & Settings Toggles
- Height 40px with 8px radius.
- Resting border `#E0E8F4`. Focus ring: 2px outer outline in `#276EF1` with zero offset.
- Checkboxes & Switches: Rounded checkboxes (4px radius) for Markdown export options (e.g., "Extract Images", "Convert Tables to HTML").

### Document Preview & Split Pane Cards
- Header containing filename, source size, conversion execution time, and quick clipboard actions.
- Content body encapsulated inside Level 1 elevation with a secondary surface toolbar for switching between Raw Markdown, Rendered HTML, and AST Tree views.