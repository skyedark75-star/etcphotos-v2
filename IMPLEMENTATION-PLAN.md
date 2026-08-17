# ETC_PHOTOS V2 implementation plan

## Retained from the current site

- ETC_PHOTOS name, automotive positioning and core business copy
- Standard (£50), Plus (£75) and Premium (£125) packages without alteration
- Package duration, image count and location limits
- Package selection followed by a customer enquiry; location and travel are discussed when arranging the shoot
- Email enquiry outcome and `contact@etcphotos.co.uk`
- Seven current portfolio groups
- Existing SEO description, organisation identity and production domain preparation
- The exact four social URLs supplied in the V2 brief

## Design system

- Warm-white editorial canvas, near-black typography and fine neutral dividers
- Photography provides nearly all interface colour; ETC red is used sparingly for orientation
- Narrow grotesque display typography with a restrained serif italic accent
- Large fluid heading scale, generous vertical rhythm and asymmetric image sequencing
- Fast transform/opacity animation with complete reduced-motion fallbacks

## Architecture

- Shared static header, mobile menu and footer are rendered by `js/site.js`
- Portfolio metadata and image orientation live in `js/projects-data.js`; Home, Work and Project pages all render from it
- `project.html?id=PROJECT_ID` creates individual project stories without duplicated gallery markup
- Booking logic is isolated in `js/booking.js`
- Everything uses relative paths and has no runtime dependencies or backend requirement

## Future additions

1. Add a project object and its optimized images to `js/projects-data.js`.
2. Verify the project sequence at desktop and mobile widths.
3. Add its canonical URL to the sitemap if dedicated static project URLs are introduced.
4. Replace or expand the current selected-image galleries with final full shoots before deployment.
