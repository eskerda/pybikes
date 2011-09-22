from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2
from station import Station

PREFIX = 'hangzhou'
URL = "http://www.hzzxc.com.cn/map/data-xml.php?"


def get_all():
  usock = urllib.urlopen(URL)
  xml_data = usock.read()
  usock.close()
  soup = BeautifulStoneSoup(xml_data.decode('gb2312','ignore').encode('utf-8'))
  sts = soup.findAll('m')
  stations = []
  for index, st in enumerate(sts):
    station = HangzhouStation(index)
    station.from_xml(st)
    stations.append(station)
  return stations
  
  
  
  
class HangzhouStation(Station):
  prefix = PREFIX
  
  def to_json(self):
    text =  '{id:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s, description:"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.description)
    return unicode(text)
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    self.name = xml_data['n']
    self.description = xml_data['p']
    self.lat = int(float(xml_data['lat'])*1E6)
    self.lng = int(float(xml_data['lng'])*1E6)