import pytest

# P0 - Critical Tests: CRUD Operations

@pytest.mark.priority_p0
class TestCriticalCRUD:
    
    # T046: Create custom prompt
    def test_create_custom_prompt(self, authenticated_client):
        client, token = authenticated_client
        response = client.post("/prompts/custom", json={
            "name": "Test Prompt",
            "prompt_text": "This is a test prompt"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Prompt"
        assert data["prompt_text"] == "This is a test prompt"
        assert "id" in data
    
    # T053: Update custom prompt
    def test_update_custom_prompt(self, authenticated_client):
        client, token = authenticated_client
        
        # Create
        create_response = client.post("/prompts/custom", json={
            "name": "Original",
            "prompt_text": "Original text"
        })
        prompt_id = create_response.json()["id"]
        
        # Update
        response = client.patch(f"/prompts/custom/{prompt_id}", json={
            "name": "Updated"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["prompt_text"] == "Original text"  # Unchanged
    
    # T061: Delete custom prompt
    def test_delete_custom_prompt(self, authenticated_client):
        client, token = authenticated_client
        
        # Create
        create_response = client.post("/prompts/custom", json={
            "name": "To Delete",
            "prompt_text": "Will be deleted"
        })
        prompt_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/prompts/custom/{prompt_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/prompts/custom/{prompt_id}")
        assert get_response.status_code == 404
    
    # T020: List system prompts
    def test_list_system_prompts(self, authenticated_client, db_session):
        from database.models import Prompt
        
        client, token = authenticated_client
        
        # Add some system prompts
        for i in range(3):
            prompt = Prompt(name=f"Prompt {i}", prompt_text=f"Text {i}")
            db_session.add(prompt)
        db_session.commit()
        
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3
    
    # T069: List user chats
    def test_list_user_chats(self, authenticated_client):
        client, token = authenticated_client
        response = client.get("/chats")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0  # No chats created yet
