from pybikes.gbfs import Gbfs, GbfsStation

class VelibStation(GbfsStation):
    def __init__(self, info, * args, ** kwargs):
        super(VelibStation, self).__init__(info, * args, ** kwargs)
        # This is the traditional code for a velib station. stationCode is not
        # on the GBFS specification. Provide stationCode as id, keep station_id
        # available.
        self.extra['uid'] = info['stationCode']
        self.extra['station_id'] = info['station_id']

        # old 'banking' field
        self.extra['banking'] = 'creditcard' in self.extra.get('payment', [])
        # new payment-terminal field
        self.extra['payment-terminal'] = self.extra['banking']

        # vehicle_types_available field. Here, we have them under a list
        # of { "name-vehicle": num }, like [{"mechanical": 5}, {"ebike": 3}]
        # just awesome

        for bt in info.get('num_bikes_available_types', []):
            if 'ebike' in bt:
                self.extra['ebikes'] = int(bt['ebike'])
            if 'mechanical' in bt:
                self.extra['normal_bikes'] = int(bt['mechanical'])


class Velib(Gbfs):
    station_cls = VelibStation
