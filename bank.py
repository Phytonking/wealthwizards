<<<<<<< Updated upstream
import requests

r = requests.post('http://127.0.0.1:8000/api/create_link_token')

print(r.json())
=======
import plaid

# Replace these with your actual Plaid API credentials
PLAID_CLIENT_ID = "64c1ec037d2ab20018140136"
PLAID_SECRET = "8e4def974d59ef8f84b39354ebd098"
PLAID_PUBLIC_KEY = "YOUR_PLAID_PUBLIC_KEY"
PLAID_ENV = "sandbox"  # Change this to "development" or "production" as needed

# Initialize Plaid client
client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

# Sample user credentials (sandbox environment)
USERNAME = "user_good"
PASSWORD = "pass_good"
INSTITUTION_ID = "ins_1"  # You can find institution IDs from Plaid's documentation

# Step 1: Create a public token (to exchange for an access token)
response = client.Sandbox.public_token.create(
    institution_id=INSTITUTION_ID,
    initial_products=["transactions"],
)
public_token = response["public_token"]

# Step 2: Exchange the public token for an access token
response = client.Item.public_token.exchange(public_token)
access_token = response["access_token"]

# Step 3: Fetch transactions for the given access token
start_date = "2023-01-01"
end_date = "2023-07-01"
response = client.Transactions.get(access_token, start_date, end_date)
transactions = response["transactions"]

# Print the fetched transactions
for transaction in transactions:
    print(f"Date: {transaction['date']}, Amount: {transaction['amount']}, Description: {transaction['name']}")
>>>>>>> Stashed changes
