import os
import io
import unittest
from datetime import datetime
from app import app
import database as db

class WasteManagementSystemTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_01_seed_and_admin_login(self):
        # Admin single user login with email
        res = self.client.post('/api/login/admin', json={
            'identifier': 'admin@ecoclean.org',
            'password': 'admin123'
        })
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('redirect'), '/admin/dashboard')

        # Admin login with phone
        res_phone = self.client.post('/api/login/admin', json={
            'identifier': '9876543210',
            'password': 'admin123'
        })
        self.assertTrue(res_phone.get_json().get('success'))

    def test_02_admin_dashboard_counts(self):
        self.client.post('/api/login/admin', json={'identifier': 'admin@ecoclean.org', 'password': 'admin123'})
        res = self.client.get('/api/admin/dashboard')
        data = res.get_json()
        self.assertTrue(data.get('success'))
        counts = data.get('counts')
        # Total numbers of = Users, Complains, Collector, Resolve complains
        self.assertIn('total_users', counts)
        self.assertIn('total_complaints', counts)
        self.assertIn('total_collectors', counts)
        self.assertIn('total_resolved', counts)
        self.assertGreater(counts['total_users'], 0)
        self.assertGreater(counts['total_complaints'], 0)
        self.assertGreater(counts['total_collectors'], 0)

    def test_03_admin_waste_area_alerts_4_colors(self):
        self.client.post('/api/login/admin', json={'identifier': 'admin@ecoclean.org', 'password': 'admin123'})
        res = self.client.get('/api/admin/waste-area-alert')
        data = res.get_json()
        self.assertTrue(data.get('success'))
        grouped = data.get('grouped')
        # 4 categories based on color: High: Red, Medium: Orange, Low: Yellow, Clear: Green
        self.assertIn('High', grouped)
        self.assertIn('Medium', grouped)
        self.assertIn('Low', grouped)
        self.assertIn('Clear', grouped)

        # Downtown Sector 1 should be High (Red)
        high_areas = [a['area_name'] for a in grouped['High']]
        self.assertIn('Downtown Sector 1', high_areas)

    def test_04_admin_loggers_and_employees_tables(self):
        self.client.post('/api/login/admin', json={'identifier': 'admin@ecoclean.org', 'password': 'admin123'})
        # Loggers (users)
        res_loggers = self.client.get('/api/admin/loggers')
        data_loggers = res_loggers.get_json()
        self.assertTrue(data_loggers.get('success'))
        self.assertGreater(len(data_loggers.get('users')), 0)
        user0 = data_loggers['users'][0]
        self.assertTrue(user0['unique_id'].startswith('USR-'))
        self.assertIn('name', user0)
        self.assertIn('age', user0)
        self.assertIn('gender', user0)
        self.assertIn('area', user0)
        self.assertIn('email', user0)
        self.assertIn('phone', user0)

        # Employees (collectors)
        res_emp = self.client.get('/api/admin/employees')
        data_emp = res_emp.get_json()
        self.assertTrue(data_emp.get('success'))
        self.assertGreater(len(data_emp.get('collectors')), 0)
        col0 = data_emp['collectors'][0]
        self.assertTrue(col0['unique_id'].startswith('COL-'))
        self.assertIn('name', col0)
        self.assertIn('gender', col0)
        self.assertIn('phone', col0)
        self.assertIn('email', col0)
        self.assertIn('area_assigned', col0)

    def test_05_user_registration_and_unique_id(self):
        test_email = f"citizen_{int(datetime.now().timestamp())}@test.com"
        test_phone = f"9{int(datetime.now().timestamp())%1000000000:09d}"
        res = self.client.post('/api/register/user', json={
            'name': 'Test Citizen',
            'age': 25,
            'area': 'Downtown Sector 1',
            'email': test_email,
            'phone': test_phone,
            'gender': 'Male',
            'password': 'testpass123'
        })
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('USR-', data.get('message'))

        # Check me
        res_me = self.client.get('/api/me')
        me_data = res_me.get_json()
        self.assertEqual(me_data.get('role'), 'user')
        self.assertTrue(me_data['data']['unique_id'].startswith('USR-'))

    def test_06_user_complaint_submission_and_sla(self):
        # Login as Aarav
        self.client.post('/api/login/user', json={'identifier': 'aarav@gmail.com', 'password': 'user123'})
        
        # Submit complaint with sample picture
        fake_image = (io.BytesIO(b"fake image binary"), "waste.jpg")
        res = self.client.post('/api/user/report', data={
            'area': 'Downtown Sector 1',
            'description': 'Automated test overflowing dumpster near central bank',
            'picture': fake_image
        }, content_type='multipart/form-data')
        
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('CMP-', data.get('complaint_id'))

        # Check complaints tracking
        res_cmp = self.client.get('/api/user/complaints')
        data_cmp = res_cmp.get_json()
        self.assertTrue(data_cmp.get('success'))
        self.assertIn('sla_time_left', data_cmp['complaints'][0])

    def test_07_user_rewards_badges(self):
        # Aarav has >25 complaints seeded, so Bronze should be unlocked
        self.client.post('/api/login/user', json={'identifier': 'aarav@gmail.com', 'password': 'user123'})
        res = self.client.get('/api/user/rewards')
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(data.get('total_complaints'), 25)
        bronze_badge = [b for b in data['badges'] if b['required'] == 25][0]
        self.assertTrue(bronze_badge['unlocked'])

    def test_08_collector_workflow_with_proof_photo_and_coins(self):
        # Login as Rajesh Kumar (Downtown Sector 1)
        self.client.post('/api/login/collector', json={'identifier': 'rajesh.col@ecoclean.org', 'password': 'col123'})
        
        # Get collector dashboard
        res_dash = self.client.get('/api/collector/dashboard')
        data_dash = res_dash.get_json()
        self.assertTrue(data_dash.get('success'))
        self.assertGreater(len(data_dash['pending_complaints']), 0)
        
        target_cmp = data_dash['pending_complaints'][0]['complaint_id']

        # Resolve complaint with photo proof
        fake_proof = (io.BytesIO(b"fake proof image data"), "resolved_spot.jpg")
        res_res = self.client.post('/api/collector/resolve-complaint', data={
            'complaint_id': target_cmp,
            'notes': 'Spot thoroughly swept and sanitized.',
            'resolved_picture': fake_proof
        }, content_type='multipart/form-data')

        data_res = res_res.get_json()
        self.assertTrue(data_res.get('success'))
        self.assertIn('Completed', data_res.get('message'))

        # Verify User received notification "Task Completed"
        self.client.post('/api/login/user', json={'identifier': 'aarav@gmail.com', 'password': 'user123'})
        res_notif = self.client.get('/api/user/notifications')
        data_notif = res_notif.get_json()
        self.assertTrue(data_notif.get('success'))
        task_completed_notifs = [n for n in data_notif['notifications'] if 'Task Completed' in n['title']]
        self.assertGreater(len(task_completed_notifs), 0)

if __name__ == '__main__':
    unittest.main()
