from devops_console_rest_api.config import environment
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer


azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=environment.AAD_OPENAPI_CLIENT_ID,
    tenant_id=environment.AAD_TENANT_ID,
    scopes={
        f"api://{environment.AAD_APP_CLIENT_ID}/user_impersonation": "user_impersonation",
    },
)
