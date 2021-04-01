# COVID-19 Vaccine Bot

This is a slack bot that runs in AWS Lambda to notify when COVID-19 vaccinations are available.


### Creating a Deployable Package for AWS Lambda

1. Install the required packages
   ```
   cd hyvee 
   pip install -r requirements.txt -t .
   
   cd spotter
   pip install -r requirements.txt -t .
   ```

2. Build the zip package
   ```
   cd hyvee
   zip -r9 ../hyvee.zip * -x "bin/*" "venv/*" requirements.txt .gitignore
   
   cd spotter
   zip -r9 ../spotter.zip * -x "bin/*" "venv/*" requirements.txt .gitignore
   ```

3. Upload the zip file to an AWS Lambda function in your desired region

### Environment Variables

| Variable | Type | Description |
| ------------- | ---- | ----------- |
| `SLACK_BOT_TOKEN` | string | Bot API Token for the Slack App. |


### AWS Lambda Event Parameters

| Parameter | Type | Description | Example |
| --------- | ---- | ----------- | ------- |
| `state` | string | Search locations within the included state. (spotter only) | `NE` |
| `radius` | integer | Search radius (in miles) for nearby pharmacies. | `10` |
| `latitude` | float | Geolocation latitude for searching nearby pharmacies. | `40.813616` |
| `longitude` | float | Geolocation longitude for searching nearby pharmacies. | `-96.7025955` |
| `channel` | string | The slack channel to send alerts to (Slack app must be added to this channel). | `#covid-vaccine-finder` |
| `test` | boolean | This is used to test the Lambda function and integration. It will always return at least one location (if any are within the searchable area). | `false` |


### Note

The APIs used to fetch appointment information are subject to change, and should not be considered "production ready".
Hy-Vee data is available in the spotter function but ignored for the time being, this prevents all notifications becoming
unavailable at once.
