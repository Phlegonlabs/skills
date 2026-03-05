## File: `docs/design.md`

Design specification covering both system-level tokens and page-level composition/behavior.

Structure:
```markdown
# {Project Name} Design Spec

## Part 1: Design System

### Color System
- Brand / primary palette
- Neutral palette
- Semantic colors (success / warning / error / info)
- State tokens (hover / active / disabled / focus)

### Typography
- Font families (primary, secondary, monospace if needed)
- Type scale (display, h1-h6, body, caption)
- Font weights and line-height rules

### Spacing System
- Base spacing unit
- Spacing scale tokens
- Layout spacing conventions (section gap, card padding, grid gutters)

### Component Design Rules
- Buttons: variants / sizes / states
- Inputs: variants / sizes / states / validation visuals
- Navigation: variants / responsive behavior
- Feedback components: toast / modal / banner states
- Any domain-specific reusable components

## Part 2: Page-Level Design

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
```
