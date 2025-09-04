# Exchange/Outlook Setup Guide

This guide walks you through setting up Microsoft Exchange/Outlook integration with EAIA (Executive AI Assistant).

## Prerequisites

- Microsoft 365 or Exchange Online account
- Azure AD tenant access (admin privileges recommended)
- EAIA project with Exchange dependencies installed

## Azure AD App Registration

### Step 1: Create Azure AD Application

1. Navigate to the [Azure Portal](https://portal.azure.com)
2. Go to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in the application details:
   - **Name**: `EAIA Exchange Integration`
   - **Supported account types**: Choose based on your organization's needs
   - **Redirect URI**: Leave blank for now (will be configured later if needed)
5. Click **Register**

### Step 2: Configure API Permissions

1. In your newly created app, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions** (for server-to-server scenarios)
5. Add the following permissions:
   - `Mail.ReadWrite` - Read and write access to user mail
   - `Mail.Send` - Send mail as a user
   - `Calendars.ReadWrite` - Read and write user calendars
   - `User.Read` - Sign in and read user profile

6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin privileges)

### Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "EAIA Integration Secret")
4. Choose an expiration period
5. Click **Add**
6. **Important**: Copy the secret value immediately - you won't be able to see it again

### Step 4: Note Required Information

From your Azure AD app, collect the following information:

- **Tenant ID**: Found in the app's **Overview** page
- **Client ID** (Application ID): Found in the app's **Overview** page  
- **Client Secret**: The value you copied in Step 3

## Environment Configuration

### Update Environment Variables

Add the following variables to your `.env` file:

```bash
# Exchange/Outlook Configuration
EXCHANGE_TENANT_ID=your-tenant-id-here
EXCHANGE_CLIENT_ID=your-client-id-here
EXCHANGE_CLIENT_SECRET=your-client-secret-here
EMAIL_PROVIDER=exchange  # Set to 'exchange' to use Exchange instead of Gmail
```

### Configuration Options

- `EXCHANGE_TENANT_ID`: Your Azure AD tenant ID
- `EXCHANGE_CLIENT_ID`: Your Azure AD application client ID
- `EXCHANGE_CLIENT_SECRET`: Your Azure AD application client secret
- `EMAIL_PROVIDER`: Set to `exchange` to use Exchange, or `gmail` for Gmail (default)

## Required Permissions and Scopes

The Exchange integration requires the following Microsoft Graph API scopes:

| Scope | Purpose | Permission Type |
|-------|---------|----------------|
| `Mail.ReadWrite` | Read and write user emails | Application |
| `Mail.Send` | Send emails on behalf of user | Application |
| `Calendars.ReadWrite` | Read and write calendar events | Application |
| `User.Read` | Read basic user profile information | Application |

## Testing the Setup

### Verify Dependencies

Run the following command to ensure all dependencies are installed:

```bash
uv install
```

### Test Import

Test that the Exchange module can be imported:

```python
from eaia.exchange import get_exchange_credentials
```

### Verify Configuration

Ensure your environment variables are properly set:

```python
import os
print("Tenant ID:", os.getenv("EXCHANGE_TENANT_ID"))
print("Client ID:", os.getenv("EXCHANGE_CLIENT_ID"))
print("Client Secret:", "***" if os.getenv("EXCHANGE_CLIENT_SECRET") else "Not set")
```

## Troubleshooting

### Common Setup Issues

#### 1. Authentication Errors

**Problem**: `AADSTS70011: The provided value for the input parameter 'scope' is not valid`

**Solution**: 
- Verify that all required API permissions are granted
- Ensure admin consent has been provided for application permissions
- Check that the scopes in your code match the permissions in Azure AD

#### 2. Permission Denied Errors

**Problem**: `Insufficient privileges to complete the operation`

**Solution**:
- Verify that admin consent has been granted for all required permissions
- Check that the user account has the necessary Exchange/mailbox permissions
- Ensure the Azure AD app has the correct permission types (Application vs Delegated)

#### 3. Tenant/Client ID Issues

**Problem**: `AADSTS90002: Tenant not found` or similar tenant-related errors

**Solution**:
- Double-check the `EXCHANGE_TENANT_ID` value in your `.env` file
- Ensure you're using the correct tenant ID from the Azure portal
- Verify the `EXCHANGE_CLIENT_ID` matches the Application ID in Azure AD

#### 4. Client Secret Issues

**Problem**: `AADSTS7000215: Invalid client secret is provided`

**Solution**:
- Verify the client secret hasn't expired
- Ensure the secret value was copied correctly (no extra spaces or characters)
- Generate a new client secret if needed

### Getting Help

If you encounter issues not covered in this troubleshooting section:

1. Check the Azure AD app registration settings
2. Verify all environment variables are correctly set
3. Review the Microsoft Graph API documentation
4. Check the application logs for detailed error messages

## Security Best Practices

1. **Secret Management**: Never commit client secrets to version control
2. **Principle of Least Privilege**: Only request the minimum required permissions
3. **Secret Rotation**: Regularly rotate client secrets before they expire
4. **Environment Isolation**: Use different Azure AD apps for development and production
5. **Monitoring**: Enable audit logging for your Azure AD applications

## Next Steps

Once your Exchange integration is set up:

1. The authentication implementation will be added in Stage 2
2. Email fetching functionality will be implemented in Stage 3
3. Email sending capabilities will be added in Stage 4
4. Calendar integration will be completed in later stages

For implementation details, refer to the staged development plan in `.plans/exchange-support/`.
