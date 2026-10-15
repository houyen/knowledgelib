---
name: Imperial Scholar Zi Wei
colors:
  surface: '#fff8f3'
  surface-dim: '#e0d9d2'
  surface-bright: '#fff8f3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#faf2eb'
  surface-container: '#f4ede6'
  surface-container-high: '#efe7e0'
  surface-container-highest: '#e9e1da'
  on-surface: '#1e1b17'
  on-surface-variant: '#58413f'
  inverse-surface: '#33302b'
  inverse-on-surface: '#f7efe8'
  outline: '#8c716e'
  outline-variant: '#e0bfbc'
  surface-tint: '#ad3031'
  primary: '#7a0412'
  on-primary: '#ffffff'
  primary-container: '#9b2226'
  on-primary-container: '#ffb0ab'
  inverse-primary: '#ffb3ae'
  secondary: '#775a19'
  on-secondary: '#ffffff'
  secondary-container: '#fed488'
  on-secondary-container: '#785a1a'
  tertiary: '#00432e'
  on-tertiary: '#ffffff'
  tertiary-container: '#075d42'
  on-tertiary-container: '#8ad3b1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad7'
  primary-fixed-dim: '#ffb3ae'
  on-primary-fixed: '#410005'
  on-primary-fixed-variant: '#8c161d'
  secondary-fixed: '#ffdea5'
  secondary-fixed-dim: '#e9c176'
  on-secondary-fixed: '#261900'
  on-secondary-fixed-variant: '#5d4201'
  tertiary-fixed: '#a7f2ce'
  tertiary-fixed-dim: '#8cd6b3'
  on-tertiary-fixed: '#002115'
  on-tertiary-fixed-variant: '#005139'
  background: '#fff8f3'
  on-background: '#1e1b17'
  surface-variant: '#e9e1da'
typography:
  display-lg:
    fontFamily: Noto Serif
    fontSize: 44px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.01em
  display-lg-mobile:
    fontFamily: Noto Serif
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
  headline-lg:
    fontFamily: Noto Serif
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Noto Serif
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Noto Serif
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  palace-title:
    fontFamily: Noto Serif
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
    letterSpacing: 0.04em
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  star-primary:
    fontFamily: Be Vietnam Pro
    fontSize: 13px
    fontWeight: '700'
    lineHeight: 18px
    letterSpacing: 0.01em
  star-secondary:
    fontFamily: Be Vietnam Pro
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  brightness-badge:
    fontFamily: Noto Serif
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
  caption:
    fontFamily: Be Vietnam Pro
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 16px
  label-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
id: self-docs/stitch-tu-vi-scholar-platform/design
canonical_question: 'Imperial Scholar Zi Wei design system: color, typography, rounded
  and spacing tokens for the Tử Vi app (Stitch export)'
aliases:
- Imperial Scholar Zi Wei design system
- Stitch DESIGN.md Imperial Scholar Zi Wei
- Design token màu sắc, typography, spacing cho ứng dụng Tử Vi
- Hệ thống thiết kế giấy dó, mực cổ, chu sa cho lá số tử vi
entity_type: specification
domain: self-docs > stitch-tu-vi-scholar-platform
last_verified: 2026-10-08
---

## Brand & Style

This design system embodies the regal gravitas and intellectual rigor of Imperial East Asian astrology. It synthesizes imperial court archival aesthetics—fine handcrafted mulberry paper (*giấy dó*), cinnabar red seal inks, and weathered bronze inlays—with the exacting visual clarity of modern analytical data visualization.

### Brand Personality & Emotional Tone
- **Archival Reverence:** Elicits the tactile serenity and timeless authority of handling an antique imperial astrological manuscript.
- **Scholarly Precision:** Replaces superstitious opacity with structured, legible, and balanced mathematical organization.
- **Imperial Restraint:** Luxurious through material warmth, micro-typography, and rhythmic spacing rather than excessive ornamentation.

### Visual Grammar & Stylistic Pillars
- **Medium & Surface:** Warm, tactile parchment layers, subtle raw paper textures, double-line rules (*song chỉ*), and geometric cloud-meander corner brackets (*hồi văn*).
- **Ink Philosophy:** Mực nho (dense pine-soot ink) for text hierarchy, vermilion cinnabar stamps (*chu sa*) for primary anchors, and antique gold leaf for orbital geometry.
- **Modern Scholarly Layout:** A crisp dual-tier visual hierarchy where structural frameworks use classical serifs, while dense celestial telemetry and astrological star data leverage high-legibility modern sans-serifs.

## Colors

The color palette is derived directly from classical imperial archives and five-element cosmological taxonomies. The default display mode is light, simulating aged handmade parchment and calligraphy ink.

### Primary, Secondary, and Neutral Foundations
- **Vermilion Cinnabar (Primary - `#9B2226`):** The definitive imperial red. Used for principal focal points, active宫 (palace) highlights, and imperial seal badges.
- **Imperial Bronze / Gold Leaf (Secondary - `#C5A059`):** Represents celestial cord lines, sacred borders, and palace cardinal anchors. Deep bronze `#8C6D37` is used for high-contrast outlines.
- **Imperial Jade (Tertiary - `#1D6A4E`):** Auspicious accenting, supportive cosmological indicators, and calm harmonic nodes.
- **Soot Ink (Neutral - `#1F1C18`):** The primary foreground color. Sub-shades include Charcoal Brown `#2E2822` for secondary typography and Muted Ink Stone `#5C5549` for tertiary captions.
- **Parchment Canvas:** Base canvas uses Deep Mulberry `#FAF7F0`, with card container fills on Warm Parchment `#F3EEDF` and recessed wells on Aged Vellum `#E8DFCE`.

### Semantic Astrological Tokens
#### Ngũ Hành (The Five Elements)
- **Kim (Metal):** `#5A6578` (Quenched Silver-Slate)
- **Mộc (Wood):** `#1D7A46` (Forest Green Pine)
- **Thủy (Water):** `#1A5FB4` (Deep Indigo Basin)
- **Hỏa (Fire):** `#BA2626` (Bright Vermilion Flame)
- **Thổ (Earth):** `#8A5A2B` (Ochre Son Soil)

#### Cát & Hung (Fortunate vs. Malefic Stars)
- **Cát Tinh (Auspicious Stars):** `#15803D` (Deep Leaf Emerald)
- **Hung / Sát Tinh (Inauspicious / Malefic Stars):** `#B91C1C` (Crimson Sanguine)
- **Trung Tính / Biến Hóa (Neutral / Dual Valence):** `#6B7280`

#### Star Brightness (Độ Sáng Tinh Tú)
- **Miếu (M - Exalted):** Solid fill, weight 700, maximum visual saturation.
- **Vượng (V - Prosperous):** Saturation 85%, weight 600.
- **Đắc (Đ - Favorable):** Saturation 70%, weight 600.
- **Bình (B - Neutral):** Saturation 50%, weight 400.
- **Hãm (H - Fallen):** Saturation 35%, weight 400, muted italicized text.

#### Ray & Aspect Lines (Tam Phương Tứ Chính)
- **Tam Hợp (Trine):** `#0F766E` (Deep Teal Ray)
- **Xung Chiếu (Opposition):** `#C2410C` (Terracotta Fire Ray)
- **Nhị Hợp (Hexagram Harmony):** `#B45309` (Amber Bronze Ray)
- **Hình / Hại (Clash / Harm):** `#7F1D1D` (Concealed Oxblood)

## Typography

The typographic hierarchy bridges ancestral manuscript presence with analytical density. 

### Font Archetypes & Responsibilities
- **Headlines & Palace Names (`Noto Serif`):** Chosen for its exceptional Vietnamese diacritic balance and traditional Sino-Vietnamese literary resonance. Used for major headers, 12 Palace denominations (Mệnh, Phụ Mẫu, Phúc Đức,...), and cyclical time stems (Can Chi).
- **Body & Data Grid (`Be Vietnam Pro`):** Engineered for Vietnamese readability at small sizes. Used for star names, chronological age counts (Đại Hạn, Tiểu Hạn), astronomical degrees, and commentary text.

### Typography Rules
- All Palace Names are set in uppercase or small caps with gentle letter spacing (`+0.04em`) to mirror stone steles.
- Brightness levels (Miếu, Vượng, Đắc, Bình, Hãm) are displayed in brackets directly adjacent to star names with a serif glyph to preserve classic catalog format (e.g., **Tử Vi** [M]).

## Layout & Spacing

The layout is grounded in the sacred 12-cell rectangular ring (*Địa Bàn*) surrounding a central 4-cell void (*Thiên Bàn*).

### Grid Models
- **Astrological Natal Chart (Desktop / Tablet):** A structured 4x4 matrix grid. The outer border consists of 12 distinct square-to-aspect cards representing the palaces (Dần through Sửu). The central 2x2 area merges into the single commanding *Thiên Bàn* summary ledger.
- **Narrative & Scholarly Analysis:** Standard 12-column fluid grid system with 24px gutters and 32px margins for analytical treatises, star commentary, and chronological fortune forecasts.

### Responsive Breakpoints & Viewport Adaptations
- **Desktop (≥ 1200px):** Full 4x4 interactive astrological chart with dynamic SVG aspect lines connecting trine and opposition palaces on hover.
- **Tablet (768px – 1199px):** Maintains the 4x4 grid layout with condensed star labels and collapsible palace detail drawers.
- **Mobile (< 768px):** The 4x4 grid transforms into a horizontal carousel of cardinal sectors, or switches to a sequential timeline view ordered by the 12 Houses from Mệnh clockwise. A persistent mini-radial map at the screen bottom keeps spatial orientation intact.

## Elevation & Depth

This system avoids synthetic floating drop-shadows, using paper layering, ink wash contrast, and metallic double-stroke framing to create dimension.

### Depth Hierarchy
- **Level 0 (Parchment Foundation):** The root canvas `#FAF7F0` features an ultra-fine tactile grain overlay.
- **Level 1 (Palace Cards / Surfaces):** Flat surface `#F3EEDF` demarcated by a 1px solid `#C5A059` border, inset with a 0.5px hairline `#8C6D37` inner boundary (Double Border / Song Chỉ).
- **Level 2 (Active or Inspected Palace):** Backed by warm ivory `#FFFDF9` with a subtle, warm amber diffuse glow: `0 4px 16px rgba(140, 109, 55, 0.12)`.
- **Level 3 (Imperial Overlays & Modals):** Semi-opaque parchment veil with low-intensity ink drop: `0 12px 32px rgba(31, 28, 24, 0.18)`, bounded by four geometric fretwork brass corners.

## Shapes

The design system favors crisp, authoritative geometry with subtle soft edges, reflecting traditional East Asian carved woodblocks and hand-cut paper.

### Shape Characteristics
- **Cards & Palace Cells:** Soft curvature (`0.25rem`) that respects traditional paper trim while avoiding sterile sharp corners.
- **Inscriptions & Seals:** Oval stamps (`pill-shaped`) for celestial branch tags, square stamps with double-ruled frames for imperial birth signs and personal Ba Zi coordinates.
- **Corner Motifs:** Structural cards incorporate an ornamental 6px corner notch or an overlaid cloud-fret (*hồi văn*) SVG corner accent.

## Components

### 1. Palace Card (Cung Vị)
- **Structure:** Encased in a double border: outer 1px bronze `#C5A059`, 2px parchment gutter, inner hairline border.
- **Header:** Palace title (e.g., PHỤ MẪU) in `Noto Serif` Bold, colored Vermilion `#9B2226` or Soot Ink `#1F1C18`, paired with the Earthly Branch (Tỵ, Ngọ, Mùi) in the right corner.
- **Body Columns:** Star entries are divided into two clear columns:
  - *Left Column:* Main Chính Tinh (Tử Vi, Thiên Phủ,...) with element pills and brightness indicators. Auspicious auxiliary stars (Văn Xương, Tả Phụ) follow in Green `#15803D`.
  - *Right Column:* Malefic stars (Kình Dương, Đà La, Hỏa Tinh) in Crimson `#B91C1C`.
- **Footer:** Đại Hạn decade interval (e.g., 24 - 33) and annual stem-branch badges aligned along the bottom edge.

### 2. Primary Buttons (Ấn Triện Action)
- **Default:** Background vermilion `#9B2226`, text `#FAF7F0`, bordered by an antique gold hairline `#C5A059`. Subtle 0.25rem border-radius.
- **Hover:** Deepened carmine `#7A1B1E` with an internal golden shimmer hairline.
- **Active / Pressed:** Translates down 1px to mimic the mechanical pressure of stamping a jade seal.

### 3. Star Chips & Elemental Tags
- Compact inline badges displaying element glyphs (Kim, Mộc, Thủy, Hỏa, Thổ).
- Uses a tinted background corresponding to the element at 12% opacity, paired with an element border and darkened foreground text for contrast.

### 4. Interactive Aspect Lines (Tam Phương Tứ Chính Overlay)
- Dynamic SVG vectors connecting the active cell to its opposite and trine cells.
- **Styles:** Trines (*Tam Hợp*) use solid 1.5px `#0F766E` with subtle animated dashes; Oppositions (*Xung Chiếu*) use 1.5px `#C2410C`. Non-related cells dim slightly to 40% opacity.

### 5. Input Fields & Selectors (Học Thuật Inputs)
- Background `#F3EEDF` set directly into the parchment.
- Bottom-border only or double-lined frame in `#C5A059`. Focus state invokes a crisp `#9B2226` outline with zero fuzzy glow.
- Font is `Be Vietnam Pro` 14px for clean modern numerical data entry (Solar/Lunar calendar conversion switches).

### 6. Archival Accordion & Commentary Panels
- Classical folding screen format (*Bình phong*). Panels expand with smooth vertical disclosure, separated by gold-leaf hairline dividers with a center floral star glyph.