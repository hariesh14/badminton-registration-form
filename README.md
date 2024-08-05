# Demo streamlit app using google sheets

#### Requirements

python 3.10
package requirements listed in requirements.txt file

#### Secrets file in .streamlit/secrets.toml

```[gcp_gsheet]
url = "your_google_sheet_url"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY
-----END PRIVATE KEY-----"""
client_email = "your_service_account_email@your_project_id.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email@your_project_id.iam.gserviceaccount.com"
```


#### Run locally

```shell
streamlit run app.py
```
