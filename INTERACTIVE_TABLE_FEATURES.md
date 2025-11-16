# Interactive Table Features

## Date: 2025-01-09

## Overview
Enhanced the distillation data input table with interactive features for improved usability and Excel integration.

## New Features

### 1. ✅ Enter Key Navigation
**Functionality**: Press Enter to automatically move to the next row
- When typing a value and pressing Enter, cursor moves to the next row in the same column
- If on the last row, pressing Enter automatically adds a new row
- Seamless data entry without using mouse

**Use Case**:
```
Type: 0 [Enter] → cursor moves to next row
Type: 50 [Enter] → cursor moves to next row
Type: 100 [Enter] → new row created, cursor moves there
```

### 2. ✅ Excel Paste Support
**Functionality**: Paste multi-row data from Excel with Ctrl+V
- Copy data from Excel (2 columns: Vol %, Temperature)
- Click on starting cell in the table
- Press Ctrl+V to paste
- Table automatically:
  - Detects number of rows in clipboard
  - Creates required rows if needed
  - Parses tab-separated values (Excel format)
  - Populates all cells with data

**Use Case**:
```
Excel Data:
0    50.5
10   75.2
30   120.5
50   165.8

Result: All 4 rows pasted into table starting from current cell
```

### 3. ✅ Right-Click Context Menu
**Functionality**: Right-click on table cells to access Copy/Paste menu
- **📋 Copy (Ctrl+C)**: Copy selected cells to clipboard in Excel format
- **📄 Paste (Ctrl+V)**: Paste data from clipboard
- **🗑️ Clear**: Clear content of selected cells

**Use Case**:
```
1. Select cells (click and drag, or Shift+Click)
2. Right-click on selection
3. Choose Copy/Paste/Clear from menu
```

### 4. ✅ Copy to Clipboard (Ctrl+C)
**Functionality**: Copy selected cells in Excel-compatible format
- Select one or more cells
- Press Ctrl+C or use right-click menu
- Data is copied as tab-separated values
- Can be pasted into Excel, Notepad, or back into the table

**Use Case**:
```
Select cells with values → Ctrl+C → paste into Excel
Result: Data appears in Excel with proper columns
```

### 5. ✅ Multi-Cell Selection
**Functionality**: Select multiple cells for batch operations
- Click and drag to select multiple cells
- Shift+Click to select range
- Ctrl+Click to select non-contiguous cells
- ExtendedSelection mode enabled

**Use Case**:
```
Click first cell → Hold Shift → Click last cell
Result: All cells in range selected for copy/clear
```

## Implementation Details

### Custom Table Class: `InteractiveTableWidget`
Created a custom QTableWidget subclass with enhanced functionality:

```python
class InteractiveTableWidget(QTableWidget):
    - show_context_menu(): Displays right-click menu
    - copy_to_clipboard(): Copies selected cells to clipboard
    - paste_from_clipboard(): Pastes data from clipboard
    - clear_selection(): Clears selected cells
    - keyPressEvent(): Handles Enter, Ctrl+C, Ctrl+V
```

### Key Methods:

#### Right-Click Context Menu
- Detects `CustomContextMenu` policy
- Creates QMenu with Copy/Paste/Clear actions
- Shows menu at cursor position
- Displays keyboard shortcuts in menu

#### Copy to Clipboard
- Gets selected cell range with `selectedRanges()`
- Builds tab-separated text (Excel format)
- Copies to system clipboard
- Preserves row/column structure

#### Paste from Clipboard
- Reads clipboard text
- Splits by newline (`\n`) for rows
- Splits by tab (`\t`) for columns
- Auto-expands table rows as needed
- Inserts data starting from current cell

#### Clear Selection
- Iterates through selected range
- Sets each cell text to empty string
- Preserves cell structure

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Enter** | Move to next row (auto-create if needed) |
| **Ctrl+C** | Copy selected cells to clipboard |
| **Ctrl+V** | Paste from clipboard |
| **Right-Click** | Show context menu |

## User Interface Changes

### Visual Enhancements:
1. **Updated Tip Label**: 
   ```
   💡 Tip: Press Enter to move to next row. Right-click for Copy/Paste menu. Ctrl+C to copy, Ctrl+V to paste.
   ```
   - Styled in italic gray text
   - Comprehensive instructions for all features

2. **Selection Mode**: Changed to `ExtendedSelection`
   - Allows selecting multiple cells
   - Click and drag to select range
   - Visual feedback on selected cells

3. **Context Menu Icons**: 
   - 📋 Copy
   - 📄 Paste
   - 🗑️ Clear

## Benefits

### Productivity Improvements:
- ⚡ **Faster data entry**: No mouse needed between rows
- 📋 **Bulk import**: Paste entire datasets from Excel instantly
- 🎯 **Fewer clicks**: Automatic row creation
- 💡 **Intuitive**: Standard keyboard shortcuts (Enter, Ctrl+C, Ctrl+V)
- 🖱️ **Right-click convenience**: Quick access to common operations
- ✂️ **Copy functionality**: Export data selections to Excel

### User Experience:
- Natural workflow matching Excel behavior
- Reduces manual row creation
- Supports both manual entry and bulk paste
- Clear visual feedback with tip label
- Context menu for discoverability
- Standard shortcuts for power users

## Excel Data Format

### Expected Clipboard Format:
```
Column1[TAB]Column2[NEWLINE]
Value1[TAB]Value2[NEWLINE]
Value3[TAB]Value4[NEWLINE]
```

### Example Excel Copy:
| Vol % | Temperature (°C) |
|-------|------------------|
| 0     | 45.5            |
| 10    | 78.2            |
| 30    | 125.3           |

When copied and pasted, creates 3 rows with all values populated.

## Technical Notes

### Qt Components Used:
- `QKeyEvent`: Keyboard event handling
- `QMenu`: Context menu
- `QAction`: Menu actions with shortcuts
- `CustomContextMenu`: Right-click menu policy
- `ExtendedSelection`: Multi-cell selection mode
- `selectedRanges()`: Get selected cell ranges
- `QApplication.clipboard()`: System clipboard access

### Event Handling:
- `Qt.Key_Return` / `Qt.Key_Enter`: Enter key detection
- `Qt.Key_V + Qt.ControlModifier`: Ctrl+V detection
- `Qt.Key_C + Qt.ControlModifier`: Ctrl+C detection
- `customContextMenuRequested`: Right-click signal

### Data Parsing:
- Tab-separated values: Excel's default column separator
- Newline-separated rows: Standard text format
- Automatic trimming: Removes whitespace
- Safe bounds checking: Only pastes within table columns

## Usage Examples

### Example 1: Quick Data Entry with Enter
```
1. Click on first cell
2. Type "0" → Press Enter
3. Type "160" → Press Enter
4. Type "10" → Press Enter
5. Type "176.7" → Press Enter
... continues to next row automatically
```

### Example 2: Paste from Excel
```
1. In Excel: Select data range (6 rows × 2 columns)
2. Copy (Ctrl+C)
3. In GUI: Click first cell of table
4. Paste (Ctrl+V)
Result: All 6 rows appear instantly
```

### Example 3: Copy Selection
```
1. Select cells (click and drag from cell 1 to cell 6)
2. Right-click → Copy (or Ctrl+C)
3. Open Excel
4. Paste (Ctrl+V)
Result: Data appears in Excel with proper structure
```

### Example 4: Clear Cells
```
1. Select unwanted cells
2. Right-click → Clear
Result: Selected cells emptied but structure preserved
```

## Testing Recommendations

### Test Cases:
1. ✅ Press Enter on middle row → moves to next row
2. ✅ Press Enter on last row → creates new row
3. ✅ Paste 1 row from Excel → 1 row created
4. ✅ Paste 10 rows from Excel → 10 rows created
5. ✅ Paste with cursor on row 5 → rows added after row 5
6. ✅ Select cells and Ctrl+C → data copied to clipboard
7. ✅ Right-click on cells → context menu appears
8. ✅ Context menu Copy → same as Ctrl+C
9. ✅ Context menu Paste → same as Ctrl+V
10. ✅ Context menu Clear → cells emptied
11. ✅ Copy from table, paste to Excel → data transfers correctly

## Future Enhancements (Optional)
- Tab key navigation between columns
- Undo/Redo support (Ctrl+Z/Ctrl+Y)
- Data validation on paste
- Highlight pasted cells temporarily
- Support for comma-separated values (CSV paste)
- Cut operation (Ctrl+X)
- Select All (Ctrl+A)
- Find/Replace functionality
