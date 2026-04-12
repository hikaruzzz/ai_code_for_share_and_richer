# 黄金行情分析系统

一个基于 Python + Vue 3 的黄金价格分析系统，支持实时行情获取、新闻聚合与情感分析、技术分析、买卖信号生成，以及历史数据复盘功能。

## 功能特性

- **实时行情**: 获取黄金期货(GC=F)和美元指数(DX-Y.NYB)的实时价格
- **多数据源支持**: 支持 Yahoo Finance、Alpha Vantage、模拟数据等多种数据源
- **历史数据**: 支持查询历史K线数据，可自定义时间范围
- **技术分析**: 计算MA/EMA/RSI/MACD/布林带等技术指标
- **相关性分析**: 分析黄金与美元指数的相关性
- **新闻情感**: 聚合财经新闻并进行情感分析
- **交易信号**: 综合技术指标和情感分析生成买卖建议
- **历史复盘**: 查看历史信号和验证准确性

## 技术栈

| 层级 | 技术 |
|-----|-----|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy |
| 前端 | Vue 3 / Vite / Element Plus / ECharts |
| 数据源 | Yahoo Finance / Alpha Vantage / 模拟数据 |
| 数据库 | SQLite |
| 分析引擎 | pandas / pandas-ta |

## 项目结构

```
gold_analyzer/
├── backend/                  # 后端服务
│   ├── app/
│   │   ├── main.py           # FastAPI入口
│   │   ├── config.py         # 配置管理
│   │   ├── api/routes/       # API路由
│   │   ├── services/         # 业务逻辑
│   │   │   ├── data_sources/ # 数据源适配器
│   │   │   ├── price_service.py
│   │   │   └── data_source_manager.py
│   │   ├── models/           # 数据模型
│   │   ├── db/               # 数据库
│   │   └── utils/            # 工具函数
│   └── requirements.txt
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── views/            # 页面
│   │   ├── api/              # API调用
│   │   └── stores/           # 状态管理
│   └── package.json
├── data/                     # 数据存储
├── docs/                     # 文档
└── scripts/                  # 启动脚本
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 1. 启动后端服务

```bash
# 进入后端目录
cd gold_analyzer/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动成功后会显示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
数据库初始化完成
```

关闭后端服务
netstat -ano | findstr ":8000"


### 2. 启动前端服务

**首次运行需要安装依赖：**

```bash
# 进入前端目录
cd gold_analyzer/frontend

# 安装依赖
npm install
```

**启动开发服务器：**

```bash
npm run dev
```

前端启动成功后会显示：
```
VITE v5.4.21  ready in 1310 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. 访问应用

| 服务 | 地址 | 说明 |
|-----|------|------|
| 前端页面 | http://localhost:5173 | 主界面 |
| 后端API文档 | http://localhost:8000/docs | Swagger UI |
| 后端根路径 | http://localhost:8000 | API状态 |

## 数据源配置

系统支持多种数据源，可在前端页面顶部选择切换：

| 数据源 | 说明 | API Key |
|-------|------|---------|
| `yahoo_finance` | Yahoo Finance (免费，15分钟延迟) | 不需要 |
| `alpha_vantage` | Alpha Vantage (500次/天) | 需要 |
| `mock` | 模拟数据 (用于演示和测试) | 不需要 |

### 设置 Alpha Vantage API Key

1. 访问 https://www.alphavantage.co/support/#api-key 获取免费API Key
2. 在前端数据源选择器中点击 Alpha Vantage
3. 输入 API Key 即可使用

## API接口

### 价格相关

```
GET /api/price/realtime?symbol=GC=F&source=mock    # 获取实时价格
GET /api/price/history?symbol=GC=F&period=1y       # 获取历史价格
GET /api/price/kline                                # 获取K线数据
GET /api/price/correlation                          # 获取相关性分析
POST /api/price/sync                                # 同步数据到数据库
```

### 数据源管理

```
GET  /api/price/sources                    # 获取数据源列表
POST /api/price/sources/switch?source=mock # 切换数据源
POST /api/price/sources/api-key            # 设置API Key
GET  /api/price/sources/check              # 检查数据源可用性
```

### 新闻相关

```
GET /api/news                            # 获取新闻列表
GET /api/news/sentiment                  # 获取情感分析
```

### 分析相关

```
GET /api/indicators                      # 获取技术指标
GET /api/signals/current                 # 获取当前信号
GET /api/analysis/report                 # 获取分析报告
```

### 复盘相关

```
GET /api/reviews                         # 获取复盘记录
POST /api/reviews                        # 创建复盘记录
GET /api/reviews/stats                   # 获取统计数据
```

## 信号生成逻辑

系统综合以下因素生成交易信号:

| 因素 | 权重 | 说明 |
|-----|------|------|
| 技术指标 | 60% | MA/RSI/MACD/布林带综合 |
| 新闻情感 | 25% | 近期新闻情感倾向 |
| 美元相关性 | 15% | 美元指数走势反向参考 |

**信号类型**:
- `STRONG_BUY` (置信度 ≥80%)
- `BUY` (置信度 ≥65%)
- `HOLD` (置信度 35%-65%)
- `SELL` (置信度 ≤35%)
- `STRONG_SELL` (置信度 ≤20%)

## 模拟数据

当 Yahoo Finance API 不可用（如限流）时，系统会自动使用模拟数据进行演示。模拟数据通过随机游走算法生成，能够展示类似真实市场的价格波动。

## 注意事项

1. **数据延迟**: Yahoo Finance 数据有15分钟延迟
2. **API限流**: 免费数据源可能被限流，建议控制请求频率
3. **仅供参考**: 本系统仅供学习研究，不构成投资建议

## 后续开发计划

- [x] 阶段一: MVP基础框架 ✅
- [x] 多数据源支持 ✅
- [ ] 阶段二: 技术分析引擎
- [ ] 阶段三: 新闻情感分析
- [ ] 阶段四: 复盘功能
- [ ] 阶段五: 性能优化和完善

## License

MIT
