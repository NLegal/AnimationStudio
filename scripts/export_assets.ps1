<#
    export_assets.ps1 - wrapper for scripts\export_assets.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\export_assets.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" export_assets @args
exit $LASTEXITCODE
