# Excel + VBA setup

`Portfolio_Pulse_Model.xlsx` is the Excel model shell. The VBA modules are stored separately in `excel/vba/` because the workbook is intentionally kept as a standard `.xlsx` during the validation stage.

After the workbook logic is validated in Excel:
1. Open `Portfolio_Pulse_Model.xlsx` in desktop Excel.
2. Save As `Portfolio_Pulse_Model.xlsm`.
3. Open the VBA editor (`Alt+F11` on Windows; Tools > Macro > Visual Basic Editor on Mac where supported).
4. Import each `.bas` file from `excel/vba/`.
5. Add buttons on the Dashboard or Portfolio sheet and assign the macros.

Current modules:
- `PortfolioChecks.bas` — verifies weights sum to 100%.
- `RefreshData.bas` — refreshes workbook data connections.
- `StressTesting.bas` — recalculates historical stress outputs.
- `ReportGenerator.bas` — refreshes and opens the dashboard; PDF export comes after validation.
