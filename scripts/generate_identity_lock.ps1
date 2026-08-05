<#
    generate_identity_lock.ps1 - wrapper for scripts\generate_identity_lock.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\generate_identity_lock.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" generate_identity_lock @args
exit $LASTEXITCODE
