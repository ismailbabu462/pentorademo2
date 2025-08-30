import requests
import sys
from datetime import datetime, timezone
import json

class PentestAPITester:
    def __init__(self, base_url="https://pentest-hub-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_project_id = None
        self.created_note_id = None
        self.created_target_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'id' in response_data:
                        print(f"   Response ID: {response_data['id']}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        if success:
            required_keys = ['total_projects', 'active_projects', 'total_notes', 'recent_projects']
            for key in required_keys:
                if key not in response:
                    print(f"❌ Missing key in dashboard stats: {key}")
                    return False
            print(f"   Stats: {response['total_projects']} projects, {response['active_projects']} active, {response['total_notes']} notes")
        return success

    def test_create_project(self):
        """Test project creation"""
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "Test project for API validation",
            "status": "planning",
            "team_members": ["tester@example.com", "pentester@example.com"]
        }
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=project_data
        )
        
        if success and 'id' in response:
            self.created_project_id = response['id']
            print(f"   Created project ID: {self.created_project_id}")
        return success

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get All Projects",
            "GET",
            "projects",
            200
        )
        if success:
            print(f"   Found {len(response)} projects")
        return success

    def test_get_project_detail(self):
        """Test getting specific project details"""
        if not self.created_project_id:
            print("❌ No project ID available for detail test")
            return False
            
        success, response = self.run_test(
            "Get Project Detail",
            "GET",
            f"projects/{self.created_project_id}",
            200
        )
        return success

    def test_update_project(self):
        """Test updating project"""
        if not self.created_project_id:
            print("❌ No project ID available for update test")
            return False
            
        update_data = {
            "status": "active",
            "description": "Updated test project description"
        }
        
        success, response = self.run_test(
            "Update Project",
            "PUT",
            f"projects/{self.created_project_id}",
            200,
            data=update_data
        )
        return success

    def test_add_target_to_project(self):
        """Test adding target to project"""
        if not self.created_project_id:
            print("❌ No project ID available for target test")
            return False
            
        target_data = {
            "target_type": "domain",
            "value": "example.com",
            "description": "Test target domain",
            "is_in_scope": True
        }
        
        success, response = self.run_test(
            "Add Target to Project",
            "POST",
            f"projects/{self.created_project_id}/targets",
            200,
            data=target_data
        )
        
        if success and 'id' in response:
            self.created_target_id = response['id']
            print(f"   Created target ID: {self.created_target_id}")
        return success

    def test_get_project_targets(self):
        """Test getting project targets"""
        if not self.created_project_id:
            print("❌ No project ID available for targets test")
            return False
            
        success, response = self.run_test(
            "Get Project Targets",
            "GET",
            f"projects/{self.created_project_id}/targets",
            200
        )
        if success:
            print(f"   Found {len(response)} targets")
        return success

    def test_create_note(self):
        """Test creating a note"""
        if not self.created_project_id:
            print("❌ No project ID available for note test")
            return False
            
        note_data = {
            "project_id": self.created_project_id,
            "title": "Test Note",
            "content": "This is a test note for API validation",
            "tags": ["test", "api"]
        }
        
        success, response = self.run_test(
            "Create Note",
            "POST",
            "notes",
            200,
            data=note_data
        )
        
        if success and 'id' in response:
            self.created_note_id = response['id']
            print(f"   Created note ID: {self.created_note_id}")
        return success

    def test_get_project_notes(self):
        """Test getting project notes"""
        if not self.created_project_id:
            print("❌ No project ID available for notes test")
            return False
            
        success, response = self.run_test(
            "Get Project Notes",
            "GET",
            f"projects/{self.created_project_id}/notes",
            200
        )
        if success:
            print(f"   Found {len(response)} notes")
        return success

    def test_get_note_detail(self):
        """Test getting specific note details"""
        if not self.created_note_id:
            print("❌ No note ID available for detail test")
            return False
            
        success, response = self.run_test(
            "Get Note Detail",
            "GET",
            f"notes/{self.created_note_id}",
            200
        )
        return success

    def test_update_note(self):
        """Test updating note"""
        if not self.created_note_id:
            print("❌ No note ID available for update test")
            return False
            
        update_data = {
            "title": "Updated Test Note",
            "content": "Updated content for test note",
            "tags": ["test", "api", "updated"]
        }
        
        success, response = self.run_test(
            "Update Note",
            "PUT",
            f"notes/{self.created_note_id}",
            200,
            data=update_data
        )
        return success

    def test_delete_target(self):
        """Test deleting target from project"""
        if not self.created_project_id or not self.created_target_id:
            print("❌ No project/target ID available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Target",
            "DELETE",
            f"projects/{self.created_project_id}/targets/{self.created_target_id}",
            200
        )
        return success

    def test_delete_note(self):
        """Test deleting note"""
        if not self.created_note_id:
            print("❌ No note ID available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Note",
            "DELETE",
            f"notes/{self.created_note_id}",
            200
        )
        return success

    def test_delete_project(self):
        """Test deleting project"""
        if not self.created_project_id:
            print("❌ No project ID available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Project",
            "DELETE",
            f"projects/{self.created_project_id}",
            200
        )
        return success

def main():
    print("🚀 Starting Emergent Pentest Suite API Tests")
    print("=" * 60)
    
    tester = PentestAPITester()
    
    # Test sequence
    test_sequence = [
        ("Dashboard Stats", tester.test_dashboard_stats),
        ("Create Project", tester.test_create_project),
        ("Get All Projects", tester.test_get_projects),
        ("Get Project Detail", tester.test_get_project_detail),
        ("Update Project", tester.test_update_project),
        ("Add Target to Project", tester.test_add_target_to_project),
        ("Get Project Targets", tester.test_get_project_targets),
        ("Create Note", tester.test_create_note),
        ("Get Project Notes", tester.test_get_project_notes),
        ("Get Note Detail", tester.test_get_note_detail),
        ("Update Note", tester.test_update_note),
        ("Delete Target", tester.test_delete_target),
        ("Delete Note", tester.test_delete_note),
        ("Delete Project", tester.test_delete_project),
    ]
    
    # Run all tests
    for test_name, test_func in test_sequence:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All API tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())