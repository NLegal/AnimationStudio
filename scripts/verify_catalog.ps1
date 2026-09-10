<#
    verify_catalog.ps1 - wrapper for scripts\verify_catalog.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\verify_catalog.ps1 [--db catalog.db]
#>

& "$PSScriptRoot\py.ps1" verify_catalog @args
exit $LASTEXITCODE