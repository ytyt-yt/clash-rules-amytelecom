from patch import patch, load_clash_rules


CLASH_RULES = load_clash_rules('clash-rules.yaml', 'user-rules.yaml')


def lambda_handler(event, context):
    params = event['queryStringParameters']
    sid = params['sid']
    token = params['token']

    mode = params.get('mode', 'blacklist')
    sub_info, cfg_yaml = patch(
        sid=sid, token=token, mode=mode, clash_rules=CLASH_RULES)
    return {
        'statusCode': 200,
        'body': cfg_yaml,
        'headers': {
            'Subscription-Userinfo': sub_info,
            'Content-Disposition':
                f"attachment; filename=AmyTelecom_Rule_{mode}.yaml",
        }
    }
