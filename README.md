# Clash Rules - AmyTelecom

Replace AmyTelecom default rules with [clash-rules](https://github.com/Loyalsoldier/clash-rules).

Both blacklist mode and whitelist mode are supported.

## Usage

### Command Line

check `python patch.py -h`

example:
```
python patch.py --url "https://api.nxtlnodes.com/Subscription/Clash?sid=<SID>&token=<TOKEN>" --mode whitelist -o OUTPUT.yaml
```

### AWS Lambda

* Zip scripts & dependencies
* Upload zip file to AWS Lambda Function
* Create a API Gateway Trigger

Your new subscription URL will be:
```
https://<ENDPOINT>.amazonaws.com/<API_URL>?sid=<SID>&token=<TOKEN>&mode=<MODE>
```

Subscription usage info is supported.
