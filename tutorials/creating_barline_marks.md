# Creating Barline Marks

## Part 1 - Mark-to-base

### Overview

This part describes how to create a mark from an existing glyph. We will be creating a mark out of the `barlineShortSingle` glyph. It will be placed above base glyphs.

### Creating the mark

1. Open `sources/Neanes.sfd` in FontForge.
2. In the file menu, choose `View -> Goto`. Type `barlineShortSingle` and click `OK`.
3. In the file menu, choose `Edit -> Copy`.
4. We will place our new glyph at `U+E219`. Click on the tile labeled `uniE219`. Then in the file menu, choose `Edit -> Paste`.
5. In the file menu, choose `Element -> Glyph Info`.
6. In the dialog, change the Glyph Name to `barlineShortSingleAbove`. Click `OK` to close the dialog.
7. Double-click the tile containing the new glyph. This opens up an outline window.
8. Right-click under the barline glyph and choose `Add Anchor`. This opens a dialog.
9. Since this is the first barline mark to be added to the font, we must create a new anchor class. Click the `New Class` button. Enter the name `barline` and click `OK`.
10. Now choose `barline` from the dropdown at the top of the dialog.
11. Select the radio button labeled `Mark`. Then click `OK` to close the dialog.
12. If necessary, adjust the anchor by clicking on it and moving it with the mouse or with the arrow keys. The anchor should be close to the bottom of the barline.

### Adding the mark to the lookup table

Before we can use this mark, we must add it to the mark-to-base lookup table.

1. From the file menu, choose `Element -> Font Info`.
2. In the dialog, choose `Lookups` from the left panel.
3. Select the `GPOS` tab.
4. Expand `'mark' Mark Positioning lookup 0` and select `'mark' Mark Positioning lookup 0-1`. Click the `Edit Data` button on the right.
5. Scroll to the bottom of the new dialog and click `New Anchor Class`. Type `barline` and press `OK` to close the dialog. Press `OK` again to close the Font Information dialog.

### Using the mark

Let's allow the mark to be placed above the yporroi.

1. In the file menu of the outline window, choose `View -> Goto`. Type `yporroi` and click `OK`.
2. Right-click above the yporroi glyph and choose `Add Anchor`.
3. Select `barline` from the dropdown at the top of the dialog. Then choose the radio button marked `Base Glyph`. Then click `OK` to close the dialog.
4. If necessary, adjust the anchor by clicking on it and moving it with the mouse or with the arrow keys.
5. To view the result, choose `Metrics -> New Metrics Window` from the outline window's file menu.
6. In the text box at the top, type `/yporroi/barlineShortSingleAbove`. You should see the yporroi with the barline above it. If you do not, make sure that `mark` is highlighted in the list on the left.
7. You can keep this window open side-by-side with the outline window. As you adjust the anchor position in the outline window, you can see the outcome in the metrics window.

## Part 2 - Mark-to-mark

### Overview

This part describes how to add a mark-to-mark anchor to the `barlineShortSingleAbove` glyph. This will allow the barline to be positioned above a gorgon.

### Creating the mark-to-mark anchor

1. Open `sources/Neanes.sfd` in FontForge.
2. In the file menu, choose `View -> Goto`. Type `barlineShortSingleAbove` and click `OK`.
3. Double-click the tile containing the glyph. This opens up an outline window.
4. Right-click under the barline glyph and choose `Add Anchor`. This opens a dialog.
5. Since this is the first barline mark-to-mark anchor to be added to the font, we must create a new anchor class. Click the `New Class` button. Enter the name `barlineAboveMark` and click `OK`.
6. Now choose `barlineAboveMark` from the dropdown at the top of the dialog.
7. Select the radio button labeled `Mark`. Then click `OK` to close the dialog.
8. If necessary, adjust the anchor by clicking on it and moving it with the mouse or with the arrow keys. The anchor should be close to the bottom of the barline.

### Adding the mark to the lookup table

Before we can use this mark, we must add it to the mark-to-base lookup table.

1. From the file menu, choose `Element -> Font Info`.
2. In the dialog, choose `Lookups` from the left panel.
3. Select the `GPOS` tab.
4. Expand `'mkmk' Mark to Mark lookup 1` and select `'mkmk' Mark to Mark lookup 1-1`. Click the `Edit Data` button on the right.
5. Scroll to the bottom of the new dialog and click `New Anchor Class`. Type `barlineAboveMark` and press `OK` to close the dialog. Press `OK` again to close the Font Information dialog.

### Using the mark

Let's allow the mark to be placed above the gorgon.

1. In the file menu of the outline window, choose `View -> Goto`. Type `gorgonAbove` and click `OK`.
2. Right-click above the gorgon glyph and choose `Add Anchor`.
3. Select `barlineAboveMark` from the dropdown at the top of the dialog. Then choose the radio button marked `Base Mark`. Then click `OK` to close the dialog.
4. If necessary, adjust the anchor by clicking on it and moving it with the mouse or with the arrow keys.
5. To view the result, choose `Metrics -> New Metrics Window` from the outline window's file menu.
6. In the text box at the top, type `/oligonKentimataBelow/gorgonAbove/barlineShortSingleAbove`. You should see the gorgon with the barline above it. If you do not, make sure that both `mark` and `mkmk` are highlighted in the list on the left.
7. You can keep this window open side-by-side with the outline window. As you adjust the anchor position in the outline window, you can see the outcome in the metrics window.
