"""Pruebas de validación de reportes enviados desde un navegador no confiable."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Auto'))
from v11_cloud_bridge import validate_cloud_report


def packet():
    return {'type':'autoos:cloud-report', 'report':{
        'id':'v11_123', 'scenario':'gps','title':'Prueba GPS',
        'actions':[{'choice':'Continuar','time':'14:30','effect':'Simulado'}],
        'initial':{'battery':85,'speed':0,'cpuLoad':30,'usedMemory':350},
        'final':{'battery':82,'speed':45,'cpuLoad':40,'usedMemory':420}}}

class CloudValidationTest(unittest.TestCase):
    def test_valid(self):
        out=validate_cloud_report(packet())
        self.assertEqual(out['report_id'],'v11_123')
        self.assertEqual(out['escenario'],'gps')
        self.assertEqual(out['bateria_final'],82)
    def test_wrong_type(self):
        x=packet();x['type']='autoos:kernel-sync'
        with self.assertRaises(ValueError):validate_cloud_report(x)
    def test_bad_id(self):
        x=packet();x['report']['id']='../../danger'
        with self.assertRaises(ValueError):validate_cloud_report(x)
    def test_unknown_scenario(self):
        x=packet();x['report']['scenario']='__proto__'
        with self.assertRaises(ValueError):validate_cloud_report(x)
    def test_oversized(self):
        x=packet();x['report']['title']='X'*31000
        with self.assertRaises(ValueError):validate_cloud_report(x)
    def test_bad_telemetry(self):
        x=packet();x['report']['initial']['battery']=True
        with self.assertRaises(ValueError):validate_cloud_report(x)
    def test_bad_actions(self):
        x=packet();x['report']['actions']='fake'
        with self.assertRaises(ValueError):validate_cloud_report(x)

if __name__ == '__main__': unittest.main()
