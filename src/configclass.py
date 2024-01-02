class Config():
    def __init__(self, config_json):
        self.email = config_json['email']
        self.gender_apikey = config_json['namsor_key']

        self.gender_src = config_json['genders']['src']
        self.gender_dst = config_json['genders']['dst']

        self.data_src = config_json['journal_data']['src']
        self.data_dst = config_json['journal_data']['dst']

        self.csv = config_json['output']['csv']
        self.map = config_json['output']['map']
        self.gender_plot = config_json['output']['gender-plot']