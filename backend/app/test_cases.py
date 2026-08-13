import os, sys, json, tempfile
from pathlib import Path

# Isolate DB for tests.
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(tempfile.gettempdir()) / 'helpdesk_improved_test.db')
os.environ['ENABLE_ANTHROPIC'] = 'false'
Path(os.environ['DATABASE_URL'].replace('sqlite:///','')).unlink(missing_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app

cases = [
('KB-1001', 'VPN drops repeatedly after a Windows update', 'Network', 'KB-1001'),
('KB-1002', 'Cannot connect to office WiFi on a new device', 'Network', 'KB-1002'),
('KB-1003', 'Slow internet speeds on company laptop', 'Network', 'KB-1003'),
('KB-1004', 'External monitor not detected after docking', 'Hardware', 'KB-1004'),
('KB-1005', 'Laptop battery draining unusually fast', 'Hardware', 'KB-1005'),
('KB-1006', 'Printer shows offline despite being powered on', 'Hardware', 'KB-1006'),
('KB-1007', 'Application crashes on launch after an update', 'Software', 'KB-1007'),
('KB-1008', 'Software license shows as expired or invalid', 'Software', 'KB-1008'),
('KB-1009', 'Locked out of account after failed login attempts', 'Access & Accounts', 'KB-1009'),
('KB-1010', 'Cannot access a shared drive or folder', 'Access & Accounts', 'KB-1010'),
('KB-1011', 'Not receiving external emails', 'Email & Collaboration', 'KB-1011'),
('KB-1012', 'Video calls freezing or dropping in meetings', 'Email & Collaboration', 'KB-1012'),
('KB-1013', 'Forgot password or password reset needed', 'Access & Accounts', 'KB-1013'),
('KB-1014', 'MFA push notification not received', 'Access & Accounts', 'KB-1014'),
('KB-1015', 'MFA code rejected or authenticator out of sync', 'Access & Accounts', 'KB-1015'),
('KB-1016', 'Application access request or permission missing', 'Access & Accounts', 'KB-1016'),
('KB-1017', 'Company portal or SSO login failure', 'Access & Accounts', 'KB-1017'),
('KB-1018', 'Shared folder access request still pending', 'Access & Accounts', 'KB-1018'),
('KB-1019', 'VPN authentication failed', 'Network', 'KB-1019'),
('KB-1020', 'Connected to WiFi but websites do not open', 'Network', 'KB-1020'),
('KB-1021', 'Ethernet connection not working', 'Network', 'KB-1021'),
('KB-1022', 'Network connection drops intermittently', 'Network', 'KB-1022'),
('KB-1023', 'Cannot access an internal company website', 'Network', 'KB-1023'),
('KB-1024', 'DNS or name resolution problem', 'Network', 'KB-1024'),
('KB-1025', 'Laptop will not turn on', 'Hardware', 'KB-1025'),
('KB-1026', 'Laptop is not charging', 'Hardware', 'KB-1026'),
('KB-1027', 'Keyboard not working', 'Hardware', 'KB-1027'),
('KB-1028', 'Mouse or trackpad not working', 'Hardware', 'KB-1028'),
('KB-1029', 'Webcam not detected', 'Hardware', 'KB-1029'),
('KB-1030', 'Microphone not detected', 'Hardware', 'KB-1030'),
('KB-1031', 'Docking station not working', 'Hardware', 'KB-1031'),
('KB-1032', 'USB device not recognized', 'Hardware', 'KB-1032'),
('KB-1033', 'Windows laptop is very slow', 'Windows & OS', 'KB-1033'),
('KB-1034', 'Windows update is stuck', 'Windows & OS', 'KB-1034'),
('KB-1035', 'Laptop freezes or becomes unresponsive', 'Windows & OS', 'KB-1035'),
('KB-1036', 'Blue screen or unexpected system crash', 'Windows & OS', 'KB-1036'),
('KB-1037', 'Windows does not boot normally', 'Windows & OS', 'KB-1037'),
('KB-1038', 'Software will not install', 'Software', 'KB-1038'),
('KB-1039', 'Outdated application needs an update', 'Software', 'KB-1039'),
('KB-1040', 'Application is extremely slow', 'Software', 'KB-1040'),
('KB-1041', 'Browser pages or web application not loading correctly', 'Software', 'KB-1041'),
('KB-1042', 'Outlook will not open', 'Email & Collaboration', 'KB-1042'),
('KB-1043', 'Emails are stuck in Outlook Outbox', 'Email & Collaboration', 'KB-1043'),
('KB-1044', 'Mailbox is full', 'Email & Collaboration', 'KB-1044'),
('KB-1045', 'Teams microphone or camera not working', 'Email & Collaboration', 'KB-1045'),
('KB-1046', 'Teams will not open or keeps crashing', 'Email & Collaboration', 'KB-1046'),
('KB-1047', 'Calendar is not syncing', 'Email & Collaboration', 'KB-1047'),
('KB-1048', 'Received a suspicious or phishing email', 'Security', 'KB-1048'),
('KB-1049', 'Clicked a suspicious link or attachment', 'Security', 'KB-1049'),
('KB-1050', 'Company laptop lost or stolen', 'Security', 'KB-1050'),
('KB-1051', 'Suspected malware or unusual computer behavior', 'Security', 'KB-1051'),
('KB-1052', 'Suspected account compromise', 'Security', 'KB-1052'),
('KB-1053', 'Suspicious USB device found', 'Security', 'KB-1053'),
]

with TestClient(app) as c:
    assert c.get('/health').status_code == 200
    kb = c.get('/api/kb').json(); assert len(kb) == 53
    results=[]
    for name, desc, category, kb_id in cases:
        r=c.post('/api/tickets',json={'title':name,'description':desc,'department':'Engineering','device':'Company laptop — Windows'})
        assert r.status_code==200, (name,r.text)
        d=r.json(); ids=[m['kb_article_id'] for m in d['kb_matches']]
        assert d['category'] in {'Network','Hardware','Software','Windows & OS','Access & Accounts','Email & Collaboration','Security','Other'}, (name,d['category'])
        assert kb_id in ids,(name,ids)
        assert d['ai_response'] and len(d['ai_response'])>80
        results.append((name,d['category'],d['priority'],d['status'],ids[0] if ids else None))
    sid='test-chat'
    for msg in ['hi','My VPN keeps disconnecting after a Windows update','I already tried the first step, but it is still happening']:
        r=c.post('/api/chat',json={'session_id':sid,'message':msg}); assert r.status_code==200,(msg,r.text)
        assert r.json()['reply']
    r=c.post('/api/chat',json={'session_id':'unknown','message':'quantum toaster telemetry failure'})
    assert r.status_code==200 and 'couldn\'t find a close' in r.json()['reply'].lower()
    r=c.get('/api/metrics'); assert r.status_code==200 and r.json()['total']==53
    print(json.dumps({'kb_count':len(kb),'ticket_cases_run':len(results),'chat_tests':'greeting + RAG + follow-up + unknown passed','metrics_total':r.json()['total']},indent=2))
