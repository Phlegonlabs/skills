## File: `docs/design.md`

Design specification covering design system tokens, component inventory, composition patterns, interactive patterns, layout system, and page-level composition/behavior.

Structure:
````markdown
# {Project Name} Design Spec

## Part 1: Design System

### Design Principles
- 3-5 project-specific design principles that guide every UI decision
- Examples: "Dense information display", "Keyboard-first interaction", "Dark mode default",
  "Progressive disclosure", "Minimal chrome — content is the UI"
- These are captured during the Step 2.8 Design Direction interview

### Color System
- Brand / primary palette
- Neutral palette
- Semantic colors (success / warning / error / info)
- State tokens (hover / active / disabled / focus)
- Status color mapping (if applicable — e.g., statuses like "active", "archived", "blocked"
  each map to a specific semantic color)
- CSS variable naming convention — use semantic token names (e.g., `--color-primary`,
  `--color-surface-raised`), never raw color values in component code
- Color space convention (e.g., OKLCH for perceptual uniformity, HSL, hex)

### Typography
- Font families (primary, secondary, monospace if needed)
- Type scale with exact class patterns — define ALL allowed text styles as a table:

| Role          | Class / Token          | Size   | Weight   | Use Case                  |
|---------------|------------------------|--------|----------|---------------------------|
| Page title    | `text-page-title`      | 1.5rem | 600      | Top-level page headings   |
| Section title | `text-section-title`   | 1.125rem | 600    | Card/panel headings       |
| Body          | `text-body`            | 0.875rem | 400    | Default paragraph text    |
| Muted         | `text-muted`           | 0.8125rem | 400   | Secondary/helper text     |
| Tiny label    | `text-tiny`            | 0.6875rem | 500   | Badges, metadata          |
| Mono          | `font-mono`            | 0.8125rem | 400   | Code, IDs, timestamps     |
| Large stat    | `text-stat`            | 1.75rem  | 700    | Dashboard KPI numbers     |

- Rule: use the established scale only — no ad-hoc font sizes or weights in component code

### Spacing System
- Base spacing unit
- Spacing scale tokens
- Layout spacing conventions (section gap, card padding, grid gutters)

### Radius & Shadows
- Border radius scale (e.g., `rounded-sm` = 4px, `rounded-md` = 6px, `rounded-lg` = 8px)
- Usage guidelines (e.g., buttons use `rounded-md`, cards use `rounded-lg`, avatars use `rounded-full`)
- Shadow constraints (e.g., max `shadow-sm` — heavy shadows look dated and break flat aesthetics)

### Component Hierarchy
- **Tier 1 — UI library primitives**: Components from the chosen UI library (e.g., shadcn/ui Button,
  Dialog, Select). Rules: do NOT modify source code of primitives; extend behavior through composition
  and wrapper components.
- **Tier 2 — Custom composites**: Project-specific components that compose Tier 1 primitives into
  domain-specific building blocks (e.g., `{Entity}Row`, `StatusBadge`, `FilterBar`).
  These define the project's unique design language.
- **Tier 3 — Page components**: Full page layouts that compose Tier 1 + Tier 2 components.
  Pages should contain layout logic and data orchestration, not raw styling.
- **When to create a component vs use utility classes directly**:
  - Create a component when: a pattern appears 3+ times, has internal state, or needs consistent
    props/API across usages
  - Use utility classes directly when: the pattern is one-off, purely visual, and unlikely to be reused

## Part 2: Component Inventory

A living registry of all UI components in the project. Update this section whenever components
are added, removed, or have their API changed.

### UI Library Primitives
List all primitives used from the chosen UI library:

| Component  | Source          | Key Props / Variants   | Notes                      |
|------------|-----------------|------------------------|----------------------------|
| Button     | {ui-lib}/button | variant, size, disabled | Primary action component   |
| Dialog     | {ui-lib}/dialog | open, onOpenChange      | All modals use this        |
| ...        | ...             | ...                    | ...                        |

### Custom Components
For each custom composite component:
- **File**: `components/{component-name}.tsx`
- **Props**: key props and their types
- **Usage**: when and where to use this component
- **Code example**: minimal usage snippet

### Layout Components
Components that define page structure (e.g., `AppShell`, `Sidebar`, `PageHeader`, `ContentPanel`).

### Dialog & Form Components
Components for data entry and confirmation flows (e.g., `ConfirmDialog`, `EntityForm`, `FilterPanel`).

### Utilities & Hooks
Shared hooks and utility functions related to UI behavior (e.g., `useMediaQuery`, `useDebounce`,
`useClickOutside`, `formatDate`).

## Part 3: Composition Patterns

Recurring multi-component patterns that must be implemented consistently across the app.

### Pattern: {Pattern Name}
- **Where used**: list pages/contexts where this pattern appears
- **Structure**: describe the component arrangement
- **Rules**: consistency constraints (e.g., "leading slot always: StatusIcon first, then PriorityIcon",
  "action buttons right-aligned in footer")
- **Code example**: show how components compose together

{Repeat for each recurring pattern}

## Part 4: Interactive Patterns

Standard conventions for interactive states across all components.

### Hover States
- Convention for hover feedback (e.g., "subtle background change `bg-muted/50`, never change text color")
- Row hover behavior for lists/tables
- Button hover behavior per variant

### Focus States
- Focus ring convention (e.g., "2px ring, `ring-ring` color, `ring-offset-2`")
- Tab order expectations for key pages
- Focus trap behavior for modals/dialogs

### Disabled States
- Visual convention (e.g., "50% opacity, `pointer-events-none`, no hover effect")
- When to disable vs hide elements

### Inline Editing
- If applicable: how inline editing works (click-to-edit, save/cancel behavior, escape key handling)

### Popover / Selector Patterns
- If applicable: how popover-based selectors work (trigger element, popover content, selection behavior,
  keyboard navigation within popovers)

## Part 5: Layout System

### Overall App Layout
```
+--------------------------------------------------+
| Header / Toolbar                                  |
+--------------------------------------------------+
| Sidebar       | Main Content Area                 |
| (if present)  | +-------------------------------+ |
|               | | Page Header                   | |
|               | +-------------------------------+ |
|               | | Content                       | |
|               | |                               | |
|               | +-------------------------------+ |
+---------------+-----------------------------------+
```
- Named zones with dimensions (e.g., sidebar: 240px fixed, main: fluid)
- Responsive behavior (e.g., sidebar collapses to icon-only at <1024px, hidden at <768px)

### Content Area Layout
- Max content width constraints (if any)
- Standard page padding / margins
- Grid system used within content area (if applicable)

## Part 6: Living Design Guide

For GUI projects, maintain a living design guide page within the application.

### Route
- `/design-guide` (or `/storybook`, or project-appropriate route)
- This page is for development reference, not end-user facing

### Rules
- When a new Tier 2 component is created → add it to the design guide page
- When a component's API changes → update its design guide entry
- The design guide page must show:
  - All Tier 2 (custom composite) components with variants and states
  - Interactive examples (not just static renders)
  - Color palette and typography scale preview

### Section Structure
Each component section in the design guide should show:
1. Component name and description
2. All variants / sizes
3. Key states (default, hover, active, disabled, loading)
4. Usage code snippet
5. Props table

## Part 7: File Conventions

### Directory Structure
- `components/ui/` — Tier 1 UI library primitives
- `components/` — Tier 2 custom composites
- `app/` or `pages/` — Tier 3 page components
- `hooks/` — shared React hooks / composables
- `lib/` or `utils/` — utility functions, API clients, formatters
- `contexts/` or `stores/` — state management (contexts, stores, atoms)
- `types/` — shared TypeScript types

### Naming Conventions
- Components: `PascalCase.tsx` (e.g., `StatusBadge.tsx`, `FilterBar.tsx`)
- Hooks: `camelCase.ts` starting with `use` (e.g., `useMediaQuery.ts`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`, `apiClient.ts`)
- Pages/routes: follow framework convention (e.g., `kebab-case` for file-based routing)

### Import Conventions
- Use path aliases (e.g., `@/components/...`, `@/lib/...`) — no deep relative imports (`../../..`)
- Group imports: external deps → internal aliases → relative imports → styles

## Part 8: Common Mistakes

Project-specific anti-patterns to avoid. Update this section as the team discovers new pitfalls.

- **Raw colors**: Never use raw color values (`#3b82f6`, `blue-500`) — always use semantic tokens
  (`--color-primary`, `text-primary`)
- **Ad-hoc typography**: Never invent font sizes or weights outside the type scale — if a new
  text style is needed, add it to the scale first
- **Heavy shadows**: Avoid `shadow-md` or larger — they look dated and break flat/modern aesthetics.
  Use `shadow-sm` max or rely on border/background contrast
- **Forgetting dark mode**: If dark mode is supported, every color choice must work in both themes —
  test both during development
- **Inline styles**: Avoid inline style objects when utility classes or tokens cover the case
- **Prop drilling for theme**: Use CSS variables or context for theming — don't pass color/spacing
  props through component trees
- **Ignoring the component hierarchy**: Don't build Tier 3 (page) logic inside Tier 2 (composite)
  components — keep composition clean

{Add project-specific anti-patterns as they are discovered}

## Part 9: Page-Level Design

### Page: {Page Name}
- Purpose
- Layout description (regions, hierarchy, responsive behavior)
- Component arrangement (major sections and key component relationships)
- Interaction behavior (primary actions, transitions, loading/empty/error handling)
- State changes (default, hover/focus, loading, success, failure)
- ASCII wireframe:
  +--------------------------------------------------+
  | Header                                           |
  +----------------------+---------------------------+
  | Sidebar              | Main content              |
  | - nav item           | - section A               |
  | - nav item           | - section B               |
  +----------------------+---------------------------+

{Repeat for each page/screen in scope}
````
