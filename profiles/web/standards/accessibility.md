# Accessibility Standards

## Semantic HTML
- Use semantic elements (`<nav>`, `<main>`, `<article>`, `<section>`)
- Use `<button>` for actions, `<a>` for navigation
- Use proper heading hierarchy (`h1` → `h2` → `h3`)
- Never skip heading levels

## ARIA Attributes
- Use ARIA only when semantic HTML is insufficient
- Always pair `aria-*` attributes with visible labels
- Use `aria-live` for dynamic content updates
- Test with screen readers (NVDA, VoiceOver)

## Keyboard Navigation
- All interactive elements must be keyboard accessible
- Use `tabIndex` only for custom interactive elements
- Implement visible focus indicators (`:focus-visible`)
- Support Escape key for closing modals/menus

## Color and Contrast
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- Never use color alone to convey information
- Support dark mode and high contrast mode
- Test with color blindness simulators

## Testing
- Run `axe-core` automated accessibility tests
- Test keyboard navigation manually
- Test with screen readers
- Use Lighthouse accessibility audit
