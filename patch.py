from copy import deepcopy
import requests
from ruamel.yaml import YAML


yaml = YAML(typ=['rt', 'string'])
yaml.indent(sequence=4, offset=2)


PROXY_NAME = 'AmyTelecom'
URL = "https://ghvpie.xyz/?"


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
        token=None,
        subscription_url=None,
        clash_rules=None,
        mode="blacklist",
        output_fn=None):

    if subscription_url is not None:
        token = subscription_url.split('/?')[-1]
    assert None not in (token, clash_rules)

    r = requests.get(URL + token)
    r.encoding = 'utf-8'
    sub_info = r.headers['subscription-userinfo']

    cfg = yaml.load(r.text.encode('utf-8'))

    cfg["dns"]["listen"] = "0.0.0.0:1053"

    cfg['rules'] = []
    if 'extra-rules' in clash_rules:
        cfg['rules'].extend(clash_rules['extra-rules'])
    cfg['rules'].extend(clash_rules[f'{mode}-rules'])

    all_rule_providers = clash_rules['rule-providers']
    if 'extra-rule-providers' in clash_rules:
        all_rule_providers.update(clash_rules['extra-rule-providers'])
    cfg['rule-providers'] = {}
    for r in cfg['rules']:
        t = r.split(',')
        if t[0] == 'RULE-SET':
            cfg['rule-providers'][t[1]] = all_rule_providers[t[1]]

    # proxy-groups
    proxy_name = cfg['proxy-groups'][0]['name']
    assert proxy_name == PROXY_NAME

    p_grps = [cfg['proxy-groups'][0]]

    if 'Auto' in cfg['proxy-groups'][1]['name']:
        p_grps.append(cfg['proxy-groups'][1])

    pg_tmpl = deepcopy(cfg['proxy-groups'][3])
    assert len(pg_tmpl['proxies']) > 5
    if pg_tmpl['proxies'][0] == PROXY_NAME and pg_tmpl['proxies'][1] == "DIRECT":
        pg_tmpl['proxies'][0], pg_tmpl['proxies'][1] = \
            pg_tmpl['proxies'][1], pg_tmpl['proxies'][0]
    if 'extra-rules' in clash_rules:
        for r in clash_rules['extra-rules']:
            epg = deepcopy(pg_tmpl)
            epg['name'] = r.split(',')[-1]
            p_grps.append(epg)

    assert cfg['proxy-groups'][-1]['name'] == 'Final'
    if mode == 'blacklist':
        cfg['proxy-groups'][-1]['name'] = 'Final-Black'
        cfg['proxy-groups'][-1]['proxies'] = \
            cfg['proxy-groups'][-1]['proxies'][::-1]
    elif mode == 'whitelist':
        cfg['proxy-groups'][-1]['name'] = 'Final-White'

    p_grps.append(cfg['proxy-groups'][-1])

    cfg['proxy-groups'] = p_grps

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
