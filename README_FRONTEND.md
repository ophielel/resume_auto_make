# AI简历智能优化助手 - 前端版本

这是一个基于AI的简历智能优化系统，包含前端Web界面和后端API服务。

## 功能特点

- 🎨 现代化的响应式Web界面
- 🤖 基于阿里云百炼平台的AI简历优化
- 📱 支持移动端和桌面端
- 💾 支持简历下载和复制
- 🔄 实时生成和预览
- 📋 标准化的简历格式输出

## 项目结构

```
resume_auto_make-master/
├── demo.py                 # 原始AI简历生成脚本
├── app.py                  # Flask后端API服务
├── run.py                  # 启动脚本
├── requirements.txt        # Python依赖
├── templates/
│   └── index.html         # 前端HTML页面
├── static/
│   ├── style.css          # 样式文件
│   └── script.js          # JavaScript交互
├── user_info.txt          # 用户信息示例
├── optimized_resume.json  # 生成的简历示例
└── README_FRONTEND.md     # 前端说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并添加阿里云百炼平台API密钥：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:5000

## 使用说明

### 前端界面

1. **填写基本信息**：在表单中输入您的个人信息
2. **生成简历**：点击"生成简历"按钮，AI将为您优化简历
3. **查看结果**：在简历展示区域查看优化后的简历
4. **下载/复制**：可以下载JSON格式的简历或复制内容

### API接口

#### 生成简历
- **URL**: `POST /api/generate-resume`
- **参数**: JSON格式的用户信息
- **返回**: 优化后的简历数据

```json
{
  "success": true,
  "data": {
    "个人信息": {...},
    "教育背景": {...},
    "工作经历": [...],
    "技能专长": [...],
    "自我评价": "..."
  }
}
```

#### 健康检查
- **URL**: `GET /api/health`
- **返回**: 服务状态信息

#### 示例数据
- **URL**: `GET /api/example`
- **返回**: 示例用户信息

## 技术栈

### 前端
- HTML5
- CSS3 (响应式设计)
- JavaScript (ES6+)
- Font Awesome 图标

### 后端
- Flask (Python Web框架)
- Flask-CORS (跨域支持)
- LangChain (AI集成)
- 阿里云百炼平台 (AI服务)

## 界面特色

- 🎨 现代化渐变背景设计
- 📱 完全响应式布局
- ⚡ 流畅的动画效果
- 🔔 实时消息提示
- 📊 结构化的简历展示
- 🎯 直观的用户交互

## 自定义配置

### 修改样式
编辑 `static/style.css` 文件来自定义界面样式。

### 修改功能
编辑 `static/script.js` 文件来添加或修改前端功能。

### 修改API
编辑 `app.py` 文件来修改后端API逻辑。

## 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **API密钥错误**
   - 检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确
   - 确保API密钥有效且有足够的调用额度

3. **端口占用**
   - 修改 `app.py` 中的端口号
   - 或停止占用5000端口的其他服务

4. **跨域问题**
   - 确保Flask-CORS已正确安装
   - 检查浏览器控制台是否有CORS错误

### 调试模式

启动时添加调试参数：

```bash
python app.py --debug
```

## 部署建议

### 生产环境部署

1. **使用Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **使用Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **环境变量配置**
   - 设置 `FLASK_ENV=production`
   - 配置生产环境的API密钥
   - 启用HTTPS

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 微信联系

---

**注意**: 请确保在使用前配置正确的API密钥，并遵守相关服务的使用条款。
