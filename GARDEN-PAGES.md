# Little garden on GitHub Pages

The public garden is a static website at https://bangahee.github.io/bangahee/.
GitHub Pages should publish the `main` branch, `/ (root)`. The `.nojekyll`
file lets GitHub serve the files directly. There is no build step or package
installation. The existing daily koi workflow continues updating `koi/pond.gif`.

The page uses `index.html`, `garden.css`, `maple-breeze.js`, the existing pond
and koi artwork, and `maple/leaves-atlas.png`. The six photographic leaf
sprites were created with the built-in imagegen tool; the prompt is recorded
in `maple/image-prompt.txt`.

The canvas layer is fixed to the viewport above every section and ignores
pointer events, so links, text selection, and page scrolling continue to work.
Leaf count adapts to viewport area and rendering resolution is capped at 2x.
Animation stops while the tab is hidden. The pause setting persists locally,
and reduced motion disables the leaves by default. Visitors can explicitly
turn them on with the leaf control. The pond also uses a still image when
reduced motion is requested.

For a local preview, run `python3 -m http.server 8765` from this directory,
then visit http://localhost:8765/.
