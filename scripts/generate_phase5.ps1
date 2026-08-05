<#
    generate_phase5.ps1 - wrapper for scripts\generate_phase5.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\generate_phase5.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" generate_phase5 @args
exit $LASTEXITCODE
