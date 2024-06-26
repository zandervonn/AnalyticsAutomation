AUS = "AUS"
NZ = "NZ"
secrets = {}

def load_properties(file_path: str) -> dict:
	properties = {}
	with open(file_path, 'r') as file:
		for line in file:
			if '=' in line:
				key, value = map(str.strip, line.split('=', 1))
				properties[key] = value
	return properties

def output_folder_path() -> str:
	return secrets['base_path'] + secrets['output_folder_path']

def template_folder_path_NZ() -> str:
	return secrets['base_path'] + secrets['template_folder_path_NZ']

def template_folder_path_AUS() -> str:
	return secrets['base_path'] + secrets['template_folder_path_AUS']

def final_output_path() -> str:
	return secrets['base_path'] + secrets['final_output_path']

def employee_mapping_path() -> str:
	return secrets['base_path'] + secrets['employee_mapping_path']

def discount_mapping_path() -> str:
	return secrets['base_path'] + secrets['discount_mapping_path']

def sending_address_AUS() -> str:
	return secrets['sending_address_AUS']

def sending_address_NZ() -> str:
	return secrets['sending_address_NZ']

# Shopify
def shopify_url() -> str:
	return secrets['shopify_url']

def shopify_password() -> str:
	return secrets['shopify_password']

def shopify_api_key() -> str:
	return secrets['shopify_api_key']

def shopify_secret_key() -> str:
	return secrets['shopify_secret_key']

def shopify_ui_username() -> str:
	return secrets['shopify_ui_username']

def shopify_ui_password() -> str:
	return secrets['shopify_ui_password']

# Starshipit
def starshipit_url() -> str:
	return secrets['starshipit_url']

def starshipit_api_key() -> str:
	return secrets['starshipit_api_key']

def starshipit_subscription_key() -> str:
	return secrets['starshipit_subscription_key']

def starshipit_username_AUS() -> str:
	return secrets['starshipit_username_AUS']

def starshipit_password_AUS() -> str:
	return secrets['starshipit_password_AUS']

def starshipit_username_NZ() -> str:
	return secrets['starshipit_username_NZ']

def starshipit_password_NZ() -> str:
	return secrets['starshipit_password_NZ']

# Cin7
def cin7_api_key_AUS() -> str:
	return secrets['cin7_api_key_AUS']

def cin7_api_key_NZ() -> str:
	return secrets['cin7_api_key_NZ']

def cin7_api_username_AUS() -> str:
	return secrets['cin7_api_username_AUS']

def cin7_api_username_NZ() -> str:
	return secrets['cin7_api_username_NZ']

def cin7_username() -> str:
	return secrets['cin7_username']

def cin7_password() -> str:
	return secrets['cin7_password']

# Meta
def meta_access_token() -> str:
	return secrets['meta_access_token']

def meta_facebook_id() -> str:
	return secrets['meta_facebook_id']

def meta_insta_id() -> str:
	return secrets['meta_insta_id']

# Google
def google_chrome_data_path() -> str:
	return secrets['base_path'] + secrets['google_chrome_data_path']

def google_credentials_path() -> str:
	return secrets['base_path'] + secrets['google_credentials_path']

def google_token_path() -> str:
	return secrets['base_path'] + secrets['google_token_path']

def google_property_id() -> str:
	return secrets['google_property_id']



