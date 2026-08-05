<#
    build_asset_sheets.ps1 - wrapper for scripts\build_asset_sheets.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\build_asset_sheets.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" build_asset_sheets @args
exit $LASTEXITCODE
