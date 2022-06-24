API_KEY = "f5c3c456eaeea3cfae87d491714fdd55"
import requests


sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
)


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())


if sports_response.status_code != 200:
    print(f'Failed to get odds: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    odds_json = sports_response.json()
    print('Number of events:', len(odds_json))
    print(odds_json)

    # Check the usage quota
    print('Remaining requests', sports_response.headers['x-requests-remaining'])
    print('Used requests', sports_response.headers['x-requests-used'])
