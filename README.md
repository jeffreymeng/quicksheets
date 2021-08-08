## Plan

### Scrolling
There will be a draggable scrollbar on the right and bottom, when necessary.
The scrollbar can be scrolled in very small (1px) increments, however
only when the scrollbar passes a certain threshold does the sheet actually scroll.
When the sheet scrolls, all cells will be essentially shifted by some number
of cells, such that cells are never cut off by the scroll. They are either
completely shown or completely hidden. This is how it works in google sheets
and excel too, I believe.
