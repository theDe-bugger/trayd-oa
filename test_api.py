import unittest
import json
import requests
from datetime import datetime, timedelta

PROD_URL = 'https://thedebugger46.pythonanywhere.com'
LOCAL_URL = 'http://127.0.0.1:5000'

class TestJobManagementAPI(unittest.TestCase):
    BASE_URL = PROD_URL # CHANGE TO BASE_URL TO TEST LOCAL CODE
    
    def setUp(self):
        # Clear any existing data (if you have a cleanup endpoint)
        pass

    def test_01_create_job(self, name="Test Job 1"):
        """Test job creation"""
        url = f"{self.BASE_URL}/jobs"
        data = {
            "name": name,
            "customer": "Test Customer",
            "startDate": "2024-03-15",
            "endDate": "2024-06-15",
            "status": "In Progress"
        }
        
        response = requests.post(url, json=data)
        print(response)
        self.assertEqual(response.status_code, 201)
        
        job = response.json()
        self.assertEqual(job['name'], data['name'])
        self.assertEqual(job['customer'], data['customer'])
        self.assertEqual(job['status'], data['status'])
        
        return job['id']  # Return job_id for use in other tests

    def test_02_get_jobs(self):
        """Test getting all jobs with various filters"""
        # Create a job first
        job_id = self.test_01_create_job()
        
        # Test different filter combinations
        test_cases = [
            "",
            "?name=Test",
            "?customer=Test Customer",
            "?status=In Progress",
            "?startAfter=2024-01-01&endBefore=2024-12-31",
            "?sortBy=name&order=desc",
            "?page=1&limit=10"
        ]
        
        for query in test_cases:
            url = f"{self.BASE_URL}/jobs{query}"
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('jobs', data)
            if 'pagination' in data:
                self.assertIn('total', data['pagination'])

    def test_03_create_worker(self):
        """Test worker creation"""
        job_id = self.test_01_create_job()
        
        url = f"{self.BASE_URL}/workers"
        data = {
            "name": "John Doe",
            "role": "Electrician",
            "jobId": job_id
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 201)
        
        worker = response.json()
        self.assertEqual(worker['name'], data['name'])
        self.assertEqual(worker['role'], data['role'])
        self.assertEqual(worker['jobId'], job_id)
        
        return worker['id']

    def test_04_bulk_create_workers(self):
        """Test bulk worker creation"""
        job_id = self.test_01_create_job()
        
        url = f"{self.BASE_URL}/workers/bulk"
        data = [
            {
                "name": "John Doe",
                "role": "Electrician",
                "jobId": job_id
            },
            {
                "name": "Jane Smith",
                "role": "Carpenter",
                "jobId": job_id
            }
        ]
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 201)
        
        workers = response.json()
        self.assertEqual(len(workers), 2)
        self.assertEqual(workers[0]['role'], "Electrician")
        self.assertEqual(workers[1]['role'], "Carpenter")

    def test_05_get_workers(self):
        """Test getting workers with filters"""
        worker_id = self.test_03_create_worker()
        
        test_cases = [
            "",
            "?name=John",
            "?role=Electrician",
            "?page=1&limit=10"
        ]
        
        for query in test_cases:
            url = f"{self.BASE_URL}/workers{query}"
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('workers', data)
            self.assertIn('pagination', data)

    def test_06_get_job_workers(self):
        """Test getting workers for a specific job"""
        job_id = self.test_01_create_job()
        self.test_03_create_worker()  # Create a worker for this job
        
        url = f"{self.BASE_URL}/jobs/{job_id}/workers"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        
        workers = response.json()
        self.assertTrue(isinstance(workers, list))
        if len(workers) > 0:
            self.assertEqual(workers[0]['jobId'], job_id)

    def test_07_get_stats(self):
        """Test getting system statistics"""
        # Create some test data first
        job_id = self.test_01_create_job()
        self.test_04_bulk_create_workers()  # Create some workers
        
        url = f"{self.BASE_URL}/stats"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertIn('jobs', stats)
        self.assertIn('workers', stats)
        self.assertIn('total', stats['jobs'])
        self.assertIn('total', stats['workers'])
        self.assertIn('byStatus', stats['jobs'])
        self.assertIn('byRole', stats['workers'])

    def test_08_delete_job(self):
        """Test job deletion"""
        job_id = self.test_01_create_job(name="Test Job Delete")
        print(job_id)
        url = f"{self.BASE_URL}/jobs/{job_id}"
        response = requests.delete(url)
        self.assertEqual(response.status_code, 204)
        
        # Verify job is deleted
        response = requests.get(f"{self.BASE_URL}/jobs?name=Test Job Delete")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['jobs']), 0)

    def test_09_error_handling(self):
        """Test error handling"""
        # Test invalid job creation
        url = f"{self.BASE_URL}/jobs"
        response = requests.post(url, json={})
        self.assertEqual(response.status_code, 400)
        
        # Test invalid worker creation
        url = f"{self.BASE_URL}/workers"
        response = requests.post(url, json={})
        self.assertEqual(response.status_code, 400)
        
        # Test non-existent job
        url = f"{self.BASE_URL}/job/99999"
        response = requests.delete(url)
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main(verbosity=2) 