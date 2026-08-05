<#
    build_world_sheets.ps1 - wrapper for scripts\build_world_sheets.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\build_world_sheets.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" build_world_sheets @args
exit $LASTEXITCODE
