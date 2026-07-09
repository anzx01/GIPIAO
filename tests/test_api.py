import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


def mock_engine():
    mock = MagicMock()
    mock._get_stock_list.return_value = ['600519.SH', '000858.SH']
    mock.fetcher.fetch_market_summary.return_value = {
        "total_stocks": 2,
        "up_count": 1,
        "down_count": 1,
        "flat_count": 0,
        "total_volume": 100,
        "total_amount": 200,
        "timestamp": "2026-01-01T00:00:00",
    }
    mock.fetcher.fetch_price_data.return_value = {}
    mock.fetcher.get_stock_info_map.return_value = {}
    mock.storage.load_latest_scores.return_value = [
        {'code': '600519.SH', 'total_score': 85, 'rank': 1}
    ]
    mock.run_daily_analysis.return_value = {
        'status': 'success',
        'data': {
            'stock_scores': [
                {'code': '600519.SH', 'total_score': 85, 'rank': 1}
            ]
        }
    }
    return mock


@pytest.fixture(autouse=True)
def _override_auth():
    """业务路由现在要求登录，测试里用假用户覆盖鉴权依赖"""
    from api.main import app
    from api.auth import get_current_active_user
    from core.models import User

    fake_user = User(
        username="test_user",
        hashed_password="x",
        is_active=True,
        is_admin=False
    )
    app.dependency_overrides[get_current_active_user] = lambda: fake_user
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


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
    
    def test_login_success(self, monkeypatch):
        from api.main import app
        import api.routes.auth as auth_routes
        from core.models import UserInDB

        monkeypatch.setattr(
            auth_routes,
            "authenticate_user",
            lambda username, password: UserInDB(
                username=username,
                hashed_password="x",
                is_active=True,
                is_admin=False,
            ),
        )
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
    
    def test_login_failure(self, monkeypatch):
        from api.main import app
        import api.routes.auth as auth_routes

        monkeypatch.setattr(auth_routes, "authenticate_user", lambda username, password: None)
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_register_duplicate(self, monkeypatch):
        from api.main import app
        import api.routes.auth as auth_routes

        fake_db = MagicMock()
        fake_db.users.find_one.return_value = {"username": "admin"}
        monkeypatch.setattr(auth_routes, "get_db", lambda: fake_db)
        
        client = TestClient(app)
        response = client.post(
            "/api/auth/register",
            json={"username": "admin", "password": "Newpassword1!"}
        )
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
