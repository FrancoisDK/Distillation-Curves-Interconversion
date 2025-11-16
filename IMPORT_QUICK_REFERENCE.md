# CSV/Excel Import Feature - Quick Reference

## Using the Feature

### Import CSV
1. Click **"📥 Import CSV"** button
2. Select your `.csv` file
3. Data auto-loads into table
4. Click **"🧮 Calculate Conversions"**

### Import Excel  
1. Click **"📥 Import Excel"** button
2. Select your `.xlsx` or `.xls` file
3. Data auto-loads into table
4. Click **"🧮 Calculate Conversions"**

## Column Names That Work

**Volume:** vol, volume, %, percentage, cut  
**Temperature:** temp, temperature, °c, celsius, deg  
**Density:** density, dens, kg/m3, kg/m (optional)

## Sample Files

Located in `examples/`:
- `sample_d86.csv` - Ready to import
- `sample_d2887.csv` - Ready to import
- `create_sample_excel.py` - Generate Excel file

## File Format

```
Volume %,Temperature C,Density kg/m3
5,150,850
10,175,850
...
```

## Auto-Detection

| Filename Contains | Detected As |
|---|---|
| d2887 | D2887 |
| tbp or atm | TBP |
| (default) | D86 |

## Troubleshooting

**"Could not auto-detect"**
→ Rename columns to include: Volume, Temp

**Data not loading**
→ Check column headers are in first row

**Wrong input type**
→ Use dropdown to select correct type

## Documentation

- **IMPORT_GUIDE.md** - Complete user guide
- **IMPORT_IMPLEMENTATION_SUMMARY.md** - Technical details
- **PHASE6_SESSION_SUMMARY.md** - Feature overview

## Testing

Run tests:
```bash
python tests/test_import_features.py
```

Expected: **14 tests pass**

## What's Included

✅ Auto-detect columns (case-insensitive)  
✅ Optional density import  
✅ Input type auto-detection  
✅ Full error handling  
✅ 14 unit tests (all passing)  
✅ Sample data files  
✅ Comprehensive documentation  

## Integration

- Works with existing calculations
- Compatible with all export formats
- Supports D86, D2887, TBP conversions
- No breaking changes to existing features

---

**Status:** Production Ready ✅  
**Commits:** a254e10, 86aa978, 654b284  
**Tested:** All 14 tests passing
