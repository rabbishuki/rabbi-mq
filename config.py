# import json
# import queutils
#
# def load_rabbit_config(key, config_path='./configMaster.json'):
#
#     with open(config_path) as fp:
#         config = json.load(fp)
#
#     if key not in config:
#         raise ValueError("{} is not found in {}".format(key, config_path))
#
#     port = config['port']
#     host = config['host']
#     required = ['id', 'url', 'data']
#
#     rabbit = {
#         'in': queutils.Channel(host, port, config[key]['in_q']),
#         'out': queutils.Channel(host, port, config[key]['out_q']),
#         'log': queutils.Channel(host, port, config['log_q']),
#         'progress': queutils.Channel(host, port, config['progress_q']),
#         'error': queutils.Channel(host, port, config['error_q'])
#     }
#
#     return required, rabbit
