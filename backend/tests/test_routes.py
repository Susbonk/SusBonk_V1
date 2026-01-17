import pytest
from database.models import Prompt
from uuid import uuid4

# P0 - Critical Tests: Route Conflicts

@pytest.mark.priority_p0
class TestRouteConflicts:
    
    # T116: GET /prompts/custom returns custom prompts list (not 404)
    def test_prompts_custom_route_works(self, authenticated_client):
        client, token = authenticated_client
        response = client.get("/prompts/custom")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    # T117: GET /prompts/{valid_uuid} returns system prompt
    def test_prompts_uuid_route_works(self, authenticated_client, db_session):
        client, token = authenticated_client
        
        # Create a system prompt
        prompt = Prompt(name="Test Prompt", prompt_text="Test text")
        db_session.add(prompt)
        db_session.commit()
        
        response = client.get(f"/prompts/{prompt.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Prompt"
    
    # T118: GET /prompts/custom/{valid_uuid} returns custom prompt
    def test_prompts_custom_uuid_route_works(self, authenticated_client):
        client, token = authenticated_client
        
        # Create a custom prompt
        create_response = client.post("/prompts/custom", json={
            "name": "My Custom Prompt",
            "prompt_text": "Custom text"
        })
        prompt_id = create_response.json()["id"]
        
        response = client.get(f"/prompts/custom/{prompt_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Custom Prompt"
    
    # T119: Verify "custom" not interpreted as UUID
    def test_custom_not_treated_as_uuid(self, authenticated_client):
        client, token = authenticated_client
        
        # This should hit /prompts/custom, not /prompts/{id}
        response = client.get("/prompts/custom")
        assert response.status_code == 200
        # Should return list structure, not single prompt
        data = response.json()
        assert isinstance(data.get("items"), list)
