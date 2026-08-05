<#
    generate_face_lock.ps1 - wrapper for scripts\generate_face_lock.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\generate_face_lock.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" generate_face_lock @args
exit $LASTEXITCODE
