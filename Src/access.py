from Src.helpers.file_helpers import find_path_upwards


def load_properties(file_path: str) -> dict:
	properties = {}
	with open(file_path, 'r') as file:
		for line in file:
			if '=' in line:
				key, value = line.strip().split('=', 1)
				properties[key] = value
	return properties

secrets = load_properties(find_path_upwards(r'config\secrets.txt'))

def output_folder_path() -> str:
	return secrets['output_folder_path']

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

def starshipit_username() -> str:
	return secrets['starshipit_username']

def starshipit_password() -> str:
	return secrets['starshipit_password']

# Cin7
def cin7_api_key_AUS() -> str:
	return secrets['cin7_api_key_AUS']

def cin7_api_key_NZ() -> str:
	return secrets['cin7_api_key_NZ']

def cin7_api_username_AUS() -> str:
	return secrets['cin7_api_username_AUS']

def cin7_api_username_NZ() -> str:
	return secrets['cin7_api_username_NZ']

# Meta
def meta_access_token() -> str:
	return secrets['meta_access_token']

def meta_facebook_id() -> str:
	return secrets['meta_facebook_id']

def meta_insta_id() -> str:
	return secrets['meta_insta_id']

# Google
def google_credentials_path() -> str:
	return secrets['google_credentials_path']

def google_token_path() -> str:
	return secrets['google_token_path']

def google_property_id() -> str:
	return secrets['google_property_id']