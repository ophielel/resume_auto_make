from flask import Flask, request, jsonify, render_template, session, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import asyncio
import json
import os
import secrets
from datetime import datetime, timedelta
from demo import optimize_resume_with_llm
from prompt_templates import build_resume_prompt
from rules_engine import validate_resume_markdown
from llm_service import generate_markdown_resume
import markdown as md
from database import db, User, WorkExperience, EducationBackground, Skill, Award, Certificate, Project, Resume, UserSession

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON响应
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///resume_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 辅助函数
def generate_session_token():
    """生成会话令牌"""
    return secrets.token_urlsafe(32)

def get_current_user():
    """获取当前用户"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not session_token:
        return None
    
    user_session = UserSession.query.filter_by(
        session_token=session_token,
        is_active=True
    ).first()
    
    if user_session and user_session.expires_at > datetime.utcnow():
        return User.query.get(user_session.user_id)
    return None

def require_auth(f):
    """需要认证的装饰器"""
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': '需要登录'}), 401
        return f(user, *args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI简历优化服务运行正常'
    })

# 用户认证相关API
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': '邮箱已存在'
            }), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'注册失败: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': '账户已被禁用'
            }), 401
        
        # 创建会话
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        db.session.add(user_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': session_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout(user):
    """用户登出"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # 禁用会话
        user_session = UserSession.query.filter_by(
            session_token=session_token,
            user_id=user.id
        ).first()
        
        if user_session:
            user_session.is_active = False
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'登出失败: {str(e)}'
        }), 500

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(user):
    """获取用户资料"""
    try:
        # 获取用户完整信息
        profile_data = user.to_dict()
        
        # 添加工作经历
        profile_data['work_experiences'] = [we.to_dict() for we in user.work_experiences]
        
        # 添加教育背景
        profile_data['education_backgrounds'] = [eb.to_dict() for eb in user.education_backgrounds]
        
        # 添加技能
        profile_data['skills'] = [skill.to_dict() for skill in user.skills]
        
        # 添加简历
        profile_data['resumes'] = [resume.to_dict() for resume in user.resumes]
        
        return jsonify({
            'success': True,
            'data': profile_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取资料失败: {str(e)}'
        }), 500

@app.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile(user):
    """更新用户资料"""
    try:
        data = request.get_json()
        
        # 更新基本信息
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'success': False,
                    'error': '邮箱已被其他用户使用'
                }), 400
            user.email = data['email']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '资料更新成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'更新资料失败: {str(e)}'
        }), 500

# 工作经历管理API
@app.route('/api/work-experiences', methods=['GET'])
@require_auth
def get_work_experiences(user):
    """获取用户工作经历"""
    try:
        experiences = [we.to_dict() for we in user.work_experiences]
        return jsonify({
            'success': True,
            'data': experiences
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取工作经历失败: {str(e)}'
        }), 500

@app.route('/api/work-experiences', methods=['POST'])
@require_auth
def create_work_experience(user):
    """创建工作经历"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['company', 'position', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 创建工作经历
        work_exp = WorkExperience(
            user_id=user.id,
            company=data['company'],
            position=data['position'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            is_current=data.get('is_current', False),
            description=data.get('description', ''),
            achievements=data.get('achievements', '')
        )
        
        db.session.add(work_exp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '工作经历创建成功',
            'data': work_exp.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建工作经历失败: {str(e)}'
        }), 500

@app.route('/api/work-experiences/<int:exp_id>', methods=['PUT'])
@require_auth
def update_work_experience(user, exp_id):
    """更新工作经历"""
    try:
        work_exp = WorkExperience.query.filter_by(id=exp_id, user_id=user.id).first()
        if not work_exp:
            return jsonify({
                'success': False,
                'error': '工作经历不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'company' in data:
            work_exp.company = data['company']
        if 'position' in data:
            work_exp.position = data['position']
        if 'start_date' in data:
            work_exp.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            work_exp.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        if 'is_current' in data:
            work_exp.is_current = data['is_current']
        if 'description' in data:
            work_exp.description = data['description']
        if 'achievements' in data:
            work_exp.achievements = data['achievements']
        
        work_exp.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '工作经历更新成功',
            'data': work_exp.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'更新工作经历失败: {str(e)}'
        }), 500

@app.route('/api/work-experiences/<int:exp_id>', methods=['DELETE'])
@require_auth
def delete_work_experience(user, exp_id):
    """删除工作经历"""
    try:
        work_exp = WorkExperience.query.filter_by(id=exp_id, user_id=user.id).first()
        if not work_exp:
            return jsonify({
                'success': False,
                'error': '工作经历不存在'
            }), 404
        
        db.session.delete(work_exp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '工作经历删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'删除工作经历失败: {str(e)}'
        }), 500

# 教育背景管理API
@app.route('/api/education', methods=['GET'])
@require_auth
def get_education_backgrounds(user):
    """获取用户教育背景"""
    try:
        educations = [eb.to_dict() for eb in user.education_backgrounds]
        return jsonify({
            'success': True,
            'data': educations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取教育背景失败: {str(e)}'
        }), 500

@app.route('/api/education', methods=['POST'])
@require_auth
def create_education_background(user):
    """创建教育背景"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['school', 'major', 'degree', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 创建教育背景
        education = EducationBackground(
            user_id=user.id,
            school=data['school'],
            major=data['major'],
            degree=data['degree'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            gpa=data.get('gpa'),
            description=data.get('description', '')
        )
        
        db.session.add(education)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '教育背景创建成功',
            'data': education.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建教育背景失败: {str(e)}'
        }), 500

# 技能管理API
@app.route('/api/skills', methods=['GET'])
@require_auth
def get_skills(user):
    """获取用户技能"""
    try:
        skills = [skill.to_dict() for skill in user.skills]
        return jsonify({
            'success': True,
            'data': skills
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取技能失败: {str(e)}'
        }), 500

@app.route('/api/skills', methods=['POST'])
@require_auth
def create_skill(user):
    """创建技能"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'category', 'proficiency_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 创建技能
        skill = Skill(
            user_id=user.id,
            name=data['name'],
            category=data['category'],
            proficiency_level=data['proficiency_level'],
            description=data.get('description', '')
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '技能创建成功',
            'data': skill.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建技能失败: {str(e)}'
        }), 500

# 简历管理API
@app.route('/api/resumes', methods=['GET'])
@require_auth
def get_resumes(user):
    """获取用户简历"""
    try:
        resumes = [resume.to_dict() for resume in user.resumes]
        return jsonify({
            'success': True,
            'data': resumes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取简历失败: {str(e)}'
        }), 500

@app.route('/api/resumes', methods=['POST'])
@require_auth
def create_resume(user):
    """创建简历"""
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('content'):
            return jsonify({
                'success': False,
                'error': '标题和内容不能为空'
            }), 400
        
        # 创建简历
        resume = Resume(
            user_id=user.id,
            title=data['title'],
            is_public=data.get('is_public', False),
            is_default=data.get('is_default', False)
        )
        resume.set_content(data['content'])
        
        # 如果设置为默认简历，取消其他简历的默认状态
        if resume.is_default:
            Resume.query.filter_by(user_id=user.id, is_default=True).update({'is_default': False})
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '简历创建成功',
            'data': resume.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建简历失败: {str(e)}'
        }), 500

@app.route('/api/example', methods=['GET'])
def get_example():
    """获取示例数据"""
    example_data = {
        "姓名": "张三",
        "年龄": "25",
        "学历": "本科",
        "工作经验": "2年软件开发经验，熟悉Python、Java等编程语言",
        "技能": "Python, JavaScript, 机器学习, 数据分析, 数据库设计",
        "自我介绍": "热爱编程，有良好的学习能力和团队合作精神",
        "申请职位": "AI工程师"
    }
    
    return jsonify({
        'success': True,
        'data': example_data
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '请求的资源不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

# 异步函数包装器
def run_async(coro):
    """运行异步函数的包装器"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

# 修改路由以支持异步
@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """同步版本的简历生成端点"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必填字段
        required_fields = ['姓名', '年龄', '学历', '毕业学校', '专业', '工作经历', '目标职位']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 调用异步函数
        optimized_resume = run_async(optimize_resume_with_llm(data))
        
        if optimized_resume:
            try:
                # 尝试解析JSON响应
                if isinstance(optimized_resume, str):
                    # 清理可能的markdown格式
                    clean_data = optimized_resume.replace("```json", "").replace("```", "").strip()
                    resume_data = json.loads(clean_data)
                else:
                    resume_data = optimized_resume
                
                return jsonify({
                    'success': True,
                    'data': resume_data,
                    'message': '简历生成成功'
                })
                
            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False,
                    'error': f'解析简历数据失败: {str(e)}',
                    'raw_response': optimized_resume
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'AI生成简历失败，请稍后重试'
            }), 500
            
    except Exception as e:
        print(f"生成简历时发生错误: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@app.route('/api/generate-resume-v2', methods=['POST'])
def generate_resume_v2():
    """基于Prompt与规则引擎的Markdown简历生成端点"""
    try:
        data = request.get_json() or {}

        # 期望字段：job_title, job_description, user_profile
        job_title = data.get('job_title')
        job_description = data.get('job_description')
        user_profile = data.get('user_profile')
        if not job_title or not job_description or not user_profile:
            return jsonify({
                'success': False,
                'error': '缺少必填字段: job_title/job_description/user_profile'
            }), 400

        style = data.get('style')
        prompt = build_resume_prompt(job_title, job_description, user_profile)
        if style:
            prompt += f"\n请采用风格: {style}。标题、层级、要点风格需体现该主题，但仍保持简洁专业。"
        markdown_resume = run_async(generate_markdown_resume(prompt))
        if not markdown_resume:
            return jsonify({
                'success': False,
                'error': 'AI生成简历失败，请稍后重试'
            }), 500

        # 规则校验
        errors = validate_resume_markdown(markdown_resume, job_description)

        return jsonify({
            'success': True,
            'data': {
                'resume_markdown': markdown_resume,
                'validation_errors': errors,
                'style': style or 'default'
            },
            'message': '简历生成完成'
        })
    except Exception as e:
        print(f"generate-resume-v2 出错: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@app.route('/api/validate-resume', methods=['POST'])
def validate_resume_api():
    """对任意Markdown简历按JD进行质量校验。"""
    try:
        data = request.get_json() or {}
        resume_markdown = data.get('resume_markdown') or ''
        job_description = data.get('job_description') or ''
        if not resume_markdown or not job_description:
            return jsonify({
                'success': False,
                'error': '缺少必填字段: resume_markdown/job_description'
            }), 400

        errors = validate_resume_markdown(resume_markdown, job_description)
        return jsonify({
            'success': True,
            'data': {
                'errors': errors
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'校验失败: {str(e)}'
        }), 500


def _render_markdown_to_html(markdown_text: str, theme: str = 'classic') -> str:
    html_content = md.markdown(markdown_text, extensions=['extra'])
    theme_class = f"theme-{theme}" if theme in ['classic', 'modern', 'minimalist'] else 'theme-classic'
    return render_template('resume_base.html', title='简历', content=f'<div class="{theme_class}">{html_content}</div>')


@app.route('/api/render-resume-html', methods=['POST'])
def render_resume_html():
    """将Markdown简历渲染为带主题的HTML"""
    try:
        data = request.get_json() or {}
        resume_markdown = data.get('resume_markdown') or ''
        theme = data.get('style') or data.get('theme') or 'classic'
        if not resume_markdown:
            return jsonify({'success': False, 'error': '缺少必填字段: resume_markdown'}), 400
        html = _render_markdown_to_html(resume_markdown, theme)
        return jsonify({'success': True, 'data': {'html': html, 'style': theme}})
    except Exception as e:
        return jsonify({'success': False, 'error': f'渲染失败: {str(e)}'}), 500


@app.route('/api/resume-pdf', methods=['POST'])
def resume_pdf():
    """将Markdown或HTML简历转换为PDF并返回下载。"""
    try:
        try:
            from weasyprint import HTML  # 延迟导入，避免环境未装依赖时报模块级错误
        except Exception:
            return jsonify({'success': False, 'error': 'WeasyPrint 未安装或依赖缺失，请先安装 weasyprint 或改用 pdfkit'}), 500

        data = request.get_json() or {}
        resume_markdown = data.get('resume_markdown')
        html_input = data.get('html')
        theme = data.get('style') or data.get('theme') or 'classic'
        if not (resume_markdown or html_input):
            return jsonify({'success': False, 'error': '需要提供 resume_markdown 或 html'}), 400

        if not html_input:
            html_input = _render_markdown_to_html(resume_markdown, theme)

        # 生成临时PDF
        pdf_bytes = HTML(string=html_input, base_url=os.getcwd()).write_pdf(stylesheets=[])
        tmp_path = os.path.join(os.getcwd(), f"resume_{int(datetime.utcnow().timestamp())}.pdf")
        with open(tmp_path, 'wb') as f:
            f.write(pdf_bytes)
        return send_file(tmp_path, mimetype='application/pdf', as_attachment=True, download_name='resume.pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': f'PDF生成失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动AI简历优化服务...")
    print("访问地址: http://localhost:5000")
    print("API文档:")
    print("  POST /api/generate-resume - 生成简历")
    print("  GET  /api/health - 健康检查")
    print("  GET  /api/example - 获取示例数据")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
