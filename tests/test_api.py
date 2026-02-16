import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


def mock_engine():
    mock = MagicMock()
    mock._get_stock_list.return_value = ['600519.SH', '000858.SH']
    mock.run_daily_analysis.return_value = {
        'status': 'success',
        'data': {
            'stock_scores': [
                {'code': '600519.SH', 'total_score': 85, 'rank': 1}
            ]
        }
    }
    return mock


class TestHealthEndpoint:
    """健康检查接口测试"""
    
    def test_root_endpoint(self):
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert 'name' in response.json()
    
    def test_health_check(self):
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'


class TestStockRoutes:
    """股票路由测试"""
    
    def test_get_stock_list(self):
        from api.main import app
        
        app.state.engine = mock_engine()
        
        client = TestClient(app)
        response = client.get("/api/stocks/list")
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
    
    def test_get_stock_scores(self):
        from api.main import app
        
        app.state.engine = mock_engine()
        
        client = TestClient(app)
        response = client.get("/api/stocks/scores?top_n=5")
        
        assert response.status_code == 200
    
    def test_get_stock_detail_not_found(self):
        from api.main import app
        
        app.state.engine = mock_engine()
        
        client = TestClient(app)
        response = client.get("/api/stocks/INVALID")
        
        assert response.status_code == 404


class TestMarketRoutes:
    """市场路由测试"""
    
    def test_get_market_summary(self):
        from api.main import app
        
        app.state.engine = mock_engine()
        
        client = TestClient(app)
        response = client.get("/api/market/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
    
    def test_get_market_indices(self):
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/api/market/indices")
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data['data']


class TestAuthRoutes:
    """认证路由测试"""
    
    def test_login_success(self):
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
    
    def test_login_failure(self):
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_register_duplicate(self):
        from api.main import app
        from api.auth import fake_users_db
        
        original_admin = fake_users_db.get('admin')
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/register",
            json={"username": "admin", "password": "newpassword"}
        )
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
