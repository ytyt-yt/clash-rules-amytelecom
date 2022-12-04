import requests
from urllib.parse import urlparse, parse_qs
from ruamel.yaml import YAML


yaml = YAML(typ=['rt', 'string'])
yaml.indent(sequence=4, offset=2)


PROXY_NAME = 'AmyTelecom'
URL = "https://api.nxtlnodes.com/Subscription/Clash"


def load_clash_rules(clash_rule_path, user_rule_path=None):
    with open(clash_rule_path, 'r') as f:
        s = f.read()
        s = s.replace('PROXY', PROXY_NAME)
        rules = yaml.load(s)
    if user_rule_path is not None:
        with open(user_rule_path, 'r') as f:
            s = f.read()
            s = s.replace('PROXY', PROXY_NAME)
            user_rules = yaml.load(s)

        rules['whitelist-rules'] = rules['whitelist-rules'][:-1] \
            + user_rules['user-rules'] + rules['whitelist-rules'][-1:]
        rules['blacklist-rules'] = rules['blacklist-rules'][:-1] \
            + user_rules['user-rules'] + rules['blacklist-rules'][-1:]
    return rules


def patch(
        sid=None, token=None,
        subscription_url=None,
        clash_rules=None,
        mode="blacklist",
        output_fn=None):

    if subscription_url is not None:
        qs = parse_qs(urlparse(subscription_url).query)
        sid = qs['sid'][0]
        token = qs['token'][0]
    assert None not in (sid, token, clash_rules)

    r = requests.get(URL, params={'sid': sid, 'token': token})
    r.encoding = 'utf-8'
    sub_info = r.headers['subscription-userinfo']

    cfg = yaml.load(r.text.encode('utf-8'))
    proxy_name = cfg['proxy-groups'][0]['name']
    assert proxy_name == PROXY_NAME

    assert cfg['proxy-groups'][-1]['name'] == 'Final'
    if mode == 'blacklist':
        cfg['proxy-groups'][-1]['name'] = 'Final-Black'
        cfg['proxy-groups'][-1]['proxies'] = \
            cfg['proxy-groups'][-1]['proxies'][::-1]
    elif mode == 'whitelist':
        cfg['proxy-groups'][-1]['name'] = 'Final-White'

    cfg['proxy-groups'] = [cfg['proxy-groups'][0], cfg['proxy-groups'][-1]]

    cfg['rule-providers'] = clash_rules['rule-providers']
    if mode == 'blacklist':
        cfg['rules'] = clash_rules['blacklist-rules']
    elif mode == 'whitelist':
        cfg['rules'] = clash_rules['whitelist-rules']

    cfg['rule-providers'] = {}
    for r in cfg['rules']:
        t = r.split(',')
        if t[0] == 'RULE-SET':
            cfg['rule-providers'][t[1]] = clash_rules['rule-providers'][t[1]]
    cfg.move_to_end('rules')

    if output_fn is not None:
        with open(output_fn, 'wb') as f:
            yaml.dump(cfg, f)

    cfg_str = yaml.dump_to_string(cfg)
    return sub_info, cfg_str


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url', type=str, help="AmyTelecom Clash Subscription URL")
    parser.add_argument(
        '--mode', type=str, default="blacklist",
        choices=['blacklist', 'whitelist'],
        help="Rule Mode: (default: blacklist)")
    parser.add_argument(
        '--output', '-o', type=str, help="Output Filename")
    args = parser.parse_args()

    rules = load_clash_rules('./clash-rules.yaml', './user-rules.yaml')
    patch(subscription_url=args.url, mode=args.mode,
          output_fn=args.output, clash_rules=rules)
