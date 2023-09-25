# Clash Rules - AmyTelecom

Replace AmyTelecom default rules with [clash-rules](https://github.com/Loyalsoldier/clash-rules).

Both blacklist mode and whitelist mode are supported.

It also supports extra rules (e.g. [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Clash)). Check [clash-rules.yaml](clash-rules.yaml) for details.


## Usage

### Command Line

check `python patch.py -h`

example:
```
python patch.py --url "https://ghvpie.xyz/?<TOKEN>" --mode whitelist -o OUTPUT.yaml
```

### AWS Lambda

* Zip scripts & dependencies
* Upload zip file to AWS Lambda Function
* Create a API Gateway Trigger

Your new subscription URL will be:
```
https://<ENDPOINT>.amazonaws.com/<API_URL>?token=<TOKEN>&mode=<MODE>
```

Subscription usage info is supported.
