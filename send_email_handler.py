import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import boto3

## NOTE: SES not available in us-west-1. I use us-west-2 for SES


def lambda_handler(event, context):
    param_dict, missing_params = validate_params(
        event,
        required_params=["Subject", "Body", "Recipients"],
        optional_params=["Email_Type"],
    )
    if missing_params:
        return package_response(f"Missing required params {missing_params}", 422)

    response = send_email(param_dict)

    if response:
        return package_response(response, 200)
    else:
        return package_response("An error has occured", 500)


######################## Standard Lambda Helpers ################################################


def validate_params(event, required_params, **kwargs):
    event = standardize_event(event)
    commom_required_params = list(set(event).intersection(required_params))
    commom_optional_params = list(set(event).intersection(kwargs.get("optional_params", [])))

    param_only_dict = {k: v for k, v in event.items() if k in required_params + kwargs.get("optional_params", [])}
    logging.info(f"Total param dict: {param_only_dict}")
    logging.info(f"Found optional params: {commom_optional_params}")

    if commom_required_params != required_params:
        missing_params = [x for x in required_params if x not in event]
        return param_only_dict, missing_params

    return param_only_dict, False


def standardize_event(event):
    if "queryStringParameters" in event:
        event.update(event["queryStringParameters"])
    elif "query" in event:
        event.update(event["query"])

    result_dict = {
        k.title().strip().replace(" ", "_"):(False if v == "false" else v)
        for (k, v) in event.items()
    }
    return result_dict


def package_response(message, status_code, **kwargs):
    return {
        "statusCode": status_code if status_code else "200",
        "body": json.dumps({"data": message}),
        "headers": {"Content-Type": "application/json"},
    }


######################### Specific to Send-Email Handler ##########################################


def send_email(param_dict):
    if isinstance(param_dict["Recipients"], str):
        param_dict["Recipients"] = [param_dict["Recipients"]]

    if param_dict.get("Email_Type", "").upper() == "HTML":
        body = {"Html": {"Data": param_dict["Body"]}}
    else:
        body = {"Text": {"Data": param_dict["Body"]}}

    try:
        response = boto3.client("ses", region_name="us-west-2").send_email(
            Source="hello@your-domain.com",
            ReplyToAddresses=["hello@your-domain.com"],
            Destination={"ToAddresses": param_dict["Recipients"]},
            Message={"Subject": {"Data": param_dict["Subject"]}, "Body": body},
        )
    except Exception as e:
        logging.error(e)
        return None

    return response
