Attribute VB_Name = "RefreshPortfolio"
Option Explicit

Public Sub RefreshPortfolio()
    On Error GoTo ErrHandler

    Dim projectPath As String
    Dim workbookPath As String
    Dim paramString As String
    Dim result As String

    If Not ValidateAllocations(False) Then Exit Sub

    projectPath = ThisWorkbook.Path

    If Right$(projectPath, 6) = "/excel" Then
        projectPath = Left$(projectPath, Len(projectPath) - 6)
    End If

    workbookPath = ThisWorkbook.FullName

    If Dir(projectPath & "/excel_bidirectional.py") = "" Then
        MsgBox "Could not find excel_bidirectional.py in:" & vbCrLf & projectPath, _
               vbCritical, "Portfolio Pulse"
        Exit Sub
    End If

    ThisWorkbook.Save

    Application.ScreenUpdating = False
    Application.StatusBar = "Portfolio Pulse: running Python analytics..."

    paramString = projectPath & "|||" & workbookPath

    result = AppleScriptTask( _
        "PortfolioPulse.scpt", _
        "runPortfolioPulse", _
        paramString _
    )

    If Left$(result, 7) = "SUCCESS" Then
        MsgBox "Portfolio analysis completed successfully." & vbCrLf & vbCrLf & _
               "Close and reopen the workbook to load the refreshed results.", _
               vbInformation, "Portfolio Pulse"
    Else
        MsgBox "Python refresh failed:" & vbCrLf & vbCrLf & result, _
               vbCritical, "Portfolio Pulse"
    End If

CleanExit:
    Application.StatusBar = False
    Application.ScreenUpdating = True
    Exit Sub

ErrHandler:
    Application.StatusBar = False
    Application.ScreenUpdating = True
    MsgBox "Refresh error: " & Err.Description, _
           vbCritical, "Portfolio Pulse"
End Sub
