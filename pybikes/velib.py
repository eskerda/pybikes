from pybikes.gbfs import Gbfs, GbfsStation

class VelibStation(GbfsStation):
    def __init__(self, info):
        super(VelibStation, self).__init__(info)
        # This is the traditional code for a velib station. stationCode is not
        # on the GBFS specification. Provide stationCode as id, keep station_id
        # available.
        self.extra['uid'] = info['stationCode']
        self.extra['station_id'] = info['station_id']

        # old 'banking' field
        self.extra['banking'] = 'creditcard' in self.extra.get('payment', [])
        # new payment-terminal field
        self.extra['payment-terminal'] = self.extra['banking']

        # electric bikes. So far I have not seen this field on other GBFS
        # systems, so we must investigate. These according to specs go to a
        # vehicle_types_available field. Here, we have them under a list
        # of { "name-vehicle": num }.

        for bt in info.get('num_bikes_available_types', []):

            if next(iter(bt)) != 'ebike':
                continue

            self.extra['ebikes'] = int(bt['ebike'])

            break


class Velib(Gbfs):
    station_cls = VelibStation
