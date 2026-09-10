<#
    train_lora.ps1 - wrapper for scripts\train_lora.py.

    Forwards all arguments to the generic runner (scripts\py.ps1), which
    resolves Python 3.14 (user AppData -> PATH) and runs from the project root.

    Usage:
      .\scripts\train_lora.ps1 [args...]
#>

& "$PSScriptRoot\py.ps1" train_lora @args
exit $LASTEXITCODE