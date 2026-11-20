"""Pruebas del envío Caja Negra -> Supabase sin realizar conexiones reales."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Auto'))
from blackbox_cloud_sync import validate_blackbox_batch, persist_blackbox_batch


def packet():
    return {'type':'autoos:blackbox-batch','requestId':'bb_test_123456',
            'events':[{'id':'session_event_001','kind':'DISPATCH','severity':'info',
                       'message':'CPU asignada al PID 103','tick':13,'batteryPct':84.5,
                       'cpuPct':65.2,'ramMb':128}]}


class Table:
    def __init__(self, db):self.db=db;self.query={};self.to_insert=None
    def select(self,*a):return self
    def contains(self,k,v):self.query=v;return self
    def limit(self,*a):return self
    def execute(self):
        if self.to_insert is not None:
            self.db.rows.append(self.to_insert)
            return SimpleNamespace(data=[self.to_insert])
        return SimpleNamespace(data=[r for r in self.db.rows if r['detalles']['autoos_id']==self.query['autoos_id']])
    def insert(self,data):
        self.to_insert=data
        return self

class DB:
    def __init__(self):self.rows=[]
    def table(self,name):
        assert name=='eventos'
        return Table(self)

class TestBlackboxCloud(unittest.TestCase):
    def test_valid_batch(self):
        _, events=validate_blackbox_batch(packet())
        self.assertEqual(events[0]['severity'],'info')
    def test_bad_packet_is_rejected(self):
        p=packet();p['events'][0]['ramMb']=-1
        with self.assertRaises(ValueError):validate_blackbox_batch(p)
    def test_duplicate_batch_is_idempotent(self):
        db=DB();state={};p=packet()
        first=persist_blackbox_batch(p,db,state,allowed=True)
        second=persist_blackbox_batch(p,db,state,allowed=True)
        self.assertTrue(first['ok']);self.assertTrue(second['ok'])
        self.assertEqual(len(db.rows),1)
        self.assertEqual(first['ackedIds'],['session_event_001'])
    def test_new_session_does_not_duplicate(self):
        db=DB();first=persist_blackbox_batch(packet(),db,{},allowed=True)
        self.assertTrue(first['ok'])
        another=persist_blackbox_batch(packet(),db,{},allowed=True)
        self.assertTrue(another['ok']);self.assertEqual(len(db.rows),1)
    def test_rbac_denies_without_writing(self):
        db=DB();result=persist_blackbox_batch(packet(),db,{},allowed=False)
        self.assertFalse(result['ok']);self.assertFalse(db.rows)
    def test_missing_client_keeps_pending(self):
        result=persist_blackbox_batch(packet(),None,{},allowed=True)
        self.assertFalse(result['ok']);self.assertEqual(result['ackedIds'],[])
    def test_partial_success_is_reported(self):
        p=packet();p['events'].append({**p['events'][0], 'id':'session_event_002'})
        class FailingTable(Table):
            def insert(self,data):
                if data['detalles']['autoos_id'].endswith('002'):raise RuntimeError('blocked')
                return super().insert(data)
        class PartialDB(DB):
            def table(self,name):return FailingTable(self)
        db=PartialDB();res=persist_blackbox_batch(p,db,{},allowed=True)
        self.assertFalse(res['ok']);self.assertEqual(res['ackedIds'],['session_event_001'])
    def test_severity_maps(self):
        p=packet();p['events'][0]['severity']='critical'
        _,ev=validate_blackbox_batch(p)
        self.assertEqual(ev[0]['severity'],'critico')

if __name__=='__main__':unittest.main()
