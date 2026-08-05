<#
    finalize_phase1.ps1 - wrapper for scripts\finalize_phase1.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\finalize_phase1.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" finalize_phase1 @args
exit $LASTEXITCODE
