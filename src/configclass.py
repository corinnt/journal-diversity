class Config():
    def __init__(self, config_json):
        def try_json(keys):
            try:
                result = config_json
                for key in keys:   
                    result = result[key]
                return result
            except KeyError as err:
                print("Check config file: " + err)

        self.email = try_json(['email'])
        self.gender_apikey = try_json(['namsor_key'])

        self.gender_src = try_json(['genders', 'src'])
        self.gender_dst = try_json(['genders', 'dst'])

        self.data_src = try_json(['journal_data', 'src'])
        self.data_dst = try_json(['journal_data', 'dst'])

        self.csv = try_json(['output', 'csv'])
        self.map = try_json(['output', 'map'])
        self.gender_plot = try_json(['output', 'gender-plot'])


