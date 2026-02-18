# 股票查询问题修复说明

## 问题描述
用户在搜索框中输入股票代码后，查询不到数据，且没有任何错误提示。

## 问题分析

### 可能的原因

1. **后端数据源问题**
   - 后端可能没有配置正确的数据源（AkShare/Tushare）
   - 数据获取失败但前端没有显示错误信息

2. **前端错误处理不完善**
   - 原代码在 `catch` 块中只打印 `console.error`，用户看不到任何提示
   - 没有区分不同类型的错误（404、网络错误、认证错误等）

3. **股票代码格式问题**
   - 用户输入的代码可能格式不正确
   - 后端验证失败但前端没有提示

## 已实施的修复

### 1. 添加错误状态管理
**文件**: `frontend/app/stocks/page.tsx`

```typescript
const [error, setError] = useState<string>("");
```

### 2. 改进错误处理逻辑
```typescript
catch (error: any) {
  console.error('Failed to fetch stock data:', error);
  let errorMessage = "查询股票数据失败";

  if (error.message) {
    if (error.message.includes('404') || error.message.includes('不存在')) {
      errorMessage = `股票代码 ${code} 不存在或暂无数据，请检查代码是否正确`;
    } else if (error.message.includes('网络')) {
      errorMessage = "网络连接失败，请检查网络设置";
    } else if (error.message.includes('401') || error.message.includes('403')) {
      errorMessage = "认证失败，请重新登录";
    } else {
      errorMessage = `查询失败: ${error.message}`;
    }
  }

  setError(errorMessage);
}
```

### 3. 添加错误提示UI
```typescript
{error && (
  <Card className="border-danger/50 bg-danger/10">
    <CardContent className="p-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-danger" />
        <p className="text-danger font-medium">{error}</p>
      </div>
    </CardContent>
  </Card>
)}
```

### 4. 添加加载状态禁用按钮
```typescript
<Button variant="outline" onClick={handleSearch} disabled={loading}>
  <Search className="h-4 w-4 mr-2" />
  搜索
</Button>
```

### 5. 清除旧错误
在每次新查询时清除之前的错误：
```typescript
const fetchStockData = async (code: string) => {
  setLoading(true);
  setError("");  // 清除旧错误
  // ...
}
```

## 如何测试修复

### 测试场景 1: 正常查询
1. 输入有效股票代码：`600519` 或 `600519.SH`
2. 点击搜索
3. 应该显示股票数据

### 测试场景 2: 无效股票代码
1. 输入无效代码：`999999`
2. 点击搜索
3. 应该显示红色错误提示：`股票代码 999999.SH 不存在或暂无数据，请检查代码是否正确`

### 测试场景 3: 网络错误
1. 断开网络或停止后端服务
2. 输入任意代码并搜索
3. 应该显示：`网络连接失败，请检查网络设置`

### 测试场景 4: 后端未启动
1. 确保后端服务未运行
2. 输入代码并搜索
3. 应该显示网络连接错误

## 后端检查清单

如果前端显示错误，请检查后端：

### 1. 检查后端是否运行
```bash
# 检查端口8001是否被占用
netstat -ano | findstr :8001

# 或访问
curl http://127.0.0.1:8001/health
```

### 2. 检查数据源配置
**文件**: `config.yaml`
```yaml
data_source:
  primary: "akshare"  # 或 "tushare"
  cache_enabled: true
  cache_ttl: 3600
```

### 3. 测试后端API
```bash
# 测试股票详情接口
curl http://127.0.0.1:8001/api/stocks/600519.SH?days=60

# 测试股票列表接口
curl http://127.0.0.1:8001/api/stocks/list
```

### 4. 检查后端日志
查看 `logs/app.log` 文件，查找错误信息：
```bash
tail -f logs/app.log
```

### 5. 检查数据获取
如果使用AkShare，测试数据获取：
```python
import akshare as ak

# 测试获取股票数据
df = ak.stock_zh_a_hist(symbol="600519", period="daily", adjust="qfq")
print(df.head())
```

## 常见问题排查

### 问题1: 显示"股票代码不存在"
**原因**:
- 股票代码输入错误
- 后端数据源没有该股票数据
- 股票已退市

**解决方案**:
- 检查股票代码是否正确（6位数字）
- 尝试其他常见股票：600519（茅台）、000858（五粮液）
- 检查后端日志确认数据源是否正常

### 问题2: 显示"网络连接失败"
**原因**:
- 后端服务未启动
- 端口配置错误
- 防火墙阻止连接

**解决方案**:
```bash
# 启动后端服务
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001

# 检查前端API配置
# 文件: frontend/lib/api.ts
# 确认: const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001';
```

### 问题3: 显示"认证失败"
**原因**:
- JWT token过期
- 未登录

**解决方案**:
- 重新登录
- 检查localStorage中的token
- 清除浏览器缓存

### 问题4: 后端返回500错误
**原因**:
- 数据源API调用失败
- 数据库连接失败
- 代码逻辑错误

**解决方案**:
1. 查看后端日志：`logs/app.log`
2. 检查数据源配置
3. 测试数据库连接
4. 检查依赖包是否安装完整

## 数据源配置说明

### 使用AkShare（免费，推荐开发环境）
```yaml
# config.yaml
data_source:
  primary: "akshare"
```

**优点**:
- 免费，无需API Key
- 数据较全面

**缺点**:
- 可能有访问限制
- 数据更新可能有延迟

### 使用Tushare（推荐生产环境）
```yaml
# config.yaml
data_source:
  primary: "tushare"
```

**配置步骤**:
1. 注册Tushare账号：https://tushare.pro/register
2. 获取API Token
3. 在 `.env` 中配置：
```env
TUSHARE_TOKEN=your_token_here
```

**优点**:
- 数据质量高
- 更新及时
- 稳定可靠

**缺点**:
- 需要注册
- 免费版有调用限制

## 性能优化建议

### 1. 添加缓存
后端已实现缓存，但可以调整TTL：
```python
# api/routes/stocks.py
@cached(ttl=300, key_prefix="stock_detail:")  # 5分钟缓存
async def get_stock_detail(...):
```

### 2. 添加请求去重
防止用户快速重复点击：
```typescript
const [isSearching, setIsSearching] = useState(false);

const handleSearch = async () => {
  if (isSearching) return;
  setIsSearching(true);

  const code = searchCode.includes('.') ? searchCode : searchCode + '.SH';
  await fetchStockData(code);

  setIsSearching(false);
};
```

### 3. 添加输入防抖
```typescript
import { useDebounce } from 'use-debounce';

const [debouncedSearchCode] = useDebounce(searchCode, 500);
```

## 总结

修复后的功能：
- ✅ 显示清晰的错误提示
- ✅ 区分不同类型的错误
- ✅ 加载时禁用搜索按钮
- ✅ 自动清除旧错误
- ✅ 友好的用户体验

用户现在可以：
1. 看到具体的错误原因
2. 知道如何解决问题
3. 获得更好的反馈体验

如果问题仍然存在，请检查后端服务和数据源配置。
