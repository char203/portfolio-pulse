Attribute VB_Name = "RefreshData"
Option Explicit

Public Sub RefreshPortfolioData()
    ThisWorkbook.RefreshAll
    Application.CalculateUntilAsyncQueriesDone
    MsgBox "Portfolio data connections refreshed.", vbInformation, "Portfolio Pulse"
End Sub
