from devops_console_rest_api.config import environment
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer


azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=environment.AAD_OPENAPI_CLIENT_ID,
    scopes={
        f"api://{environment.AAD_APP_CLIENT_ID}/user_impersonation": "user_impersonation",
    },
    validate_iss=False,
)
