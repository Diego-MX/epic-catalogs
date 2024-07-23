

# May need to set policy.
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

conda deactivate
conda activate webapp

$env:ENV_TYPE='dev'
$env:SERVER_TYPE='local'

