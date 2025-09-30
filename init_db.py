"""
数据库初始化脚本
"""

import os
from datetime import datetime, timedelta
from app import app, db
from database import User, WorkExperience, EducationBackground, Skill, Resume, UserSession

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 创建示例用户
        create_sample_data()
        print("✓ 示例数据创建成功")

def create_sample_data():
    """创建示例数据"""
    # 检查是否已有用户
    if User.query.first():
        print("数据库已有数据，跳过示例数据创建")
        return
    
    # 创建示例用户
    user1 = User(
        username='demo_user',
        email='demo@example.com',
        full_name='张三',
        phone='138-0000-0000'
    )
    user1.set_password('123456')
    
    user2 = User(
        username='test_user',
        email='test@example.com',
        full_name='李四',
        phone='139-0000-0000'
    )
    user2.set_password('123456')
    
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    
    # 为user1添加工作经历
    work1 = WorkExperience(
        user_id=user1.id,
        company='北京科技有限公司',
        position='软件工程师',
        start_date=datetime(2022, 1, 1).date(),
        end_date=datetime(2023, 12, 31).date(),
        description='负责Web应用开发和维护，使用Python Flask框架',
        achievements='成功开发了3个Web应用，提升了系统性能30%'
    )
    
    work2 = WorkExperience(
        user_id=user1.id,
        company='上海互联网公司',
        position='高级软件工程师',
        start_date=datetime(2024, 1, 1).date(),
        is_current=True,
        description='负责AI相关项目开发，使用机器学习技术',
        achievements='主导开发了智能推荐系统，用户满意度提升25%'
    )
    
    db.session.add(work1)
    db.session.add(work2)
    
    # 为user1添加教育背景
    education1 = EducationBackground(
        user_id=user1.id,
        school='北京邮电大学',
        major='计算机科学与技术',
        degree='本科',
        start_date=datetime(2018, 9, 1).date(),
        end_date=datetime(2022, 6, 30).date(),
        gpa=3.8,
        description='主修计算机科学，辅修人工智能'
    )
    
    db.session.add(education1)
    
    # 为user1添加技能
    skills_data = [
        {'name': 'Python', 'category': '编程语言', 'proficiency_level': '高级'},
        {'name': 'JavaScript', 'category': '编程语言', 'proficiency_level': '中级'},
        {'name': 'Flask', 'category': '框架', 'proficiency_level': '高级'},
        {'name': 'Django', 'category': '框架', 'proficiency_level': '中级'},
        {'name': 'MySQL', 'category': '数据库', 'proficiency_level': '中级'},
        {'name': 'Redis', 'category': '数据库', 'proficiency_level': '初级'},
        {'name': 'Git', 'category': '工具', 'proficiency_level': '高级'},
        {'name': 'Docker', 'category': '工具', 'proficiency_level': '中级'},
        {'name': '机器学习', 'category': '技术', 'proficiency_level': '中级'},
        {'name': '深度学习', 'category': '技术', 'proficiency_level': '初级'}
    ]
    
    for skill_data in skills_data:
        skill = Skill(
            user_id=user1.id,
            name=skill_data['name'],
            category=skill_data['category'],
            proficiency_level=skill_data['proficiency_level'],
            description=f'熟练掌握{skill_data["name"]}，{skill_data["proficiency_level"]}水平'
        )
        db.session.add(skill)
    
    # 为user1添加示例简历
    sample_resume = {
        "个人信息": {
            "姓名": "张三",
            "年龄": "25",
            "联系方式": "138-0000-0000",
            "邮箱": "demo@example.com"
        },
        "教育背景": {
            "学历": "本科",
            "学校": "北京邮电大学",
            "专业": "计算机科学与技术",
            "时间": "2018.09 - 2022.06"
        },
        "工作经历": [
            {
                "公司": "上海互联网公司",
                "职位": "高级软件工程师",
                "时间": "2024.01 - 至今",
                "工作内容": "负责AI相关项目开发，使用机器学习技术，主导开发了智能推荐系统"
            },
            {
                "公司": "北京科技有限公司",
                "职位": "软件工程师",
                "时间": "2022.01 - 2023.12",
                "工作内容": "负责Web应用开发和维护，使用Python Flask框架"
            }
        ],
        "技能专长": [
            "熟练掌握Python、JavaScript等编程语言",
            "熟悉Flask、Django等Web框架",
            "具备MySQL、Redis等数据库使用经验",
            "熟练使用Git、Docker等开发工具",
            "了解机器学习和深度学习技术"
        ],
        "自我评价": "热爱编程，具备扎实的技术功底和持续学习能力。在AI与Web开发方向有深入实践，工作认真负责，善于团队协作。"
    }
    
    resume1 = Resume(
        user_id=user1.id,
        title='张三-软件工程师简历',
        is_default=True
    )
    resume1.set_content(sample_resume)
    db.session.add(resume1)
    
    # 为user2添加基本信息
    work3 = WorkExperience(
        user_id=user2.id,
        company='深圳科技公司',
        position='产品经理',
        start_date=datetime(2021, 6, 1).date(),
        is_current=True,
        description='负责产品规划和需求分析，协调开发团队',
        achievements='成功推出了2款产品，用户增长50%'
    )
    
    education2 = EducationBackground(
        user_id=user2.id,
        school='清华大学',
        major='工商管理',
        degree='硕士',
        start_date=datetime(2019, 9, 1).date(),
        end_date=datetime(2021, 6, 30).date(),
        gpa=3.9
    )
    
    db.session.add(work3)
    db.session.add(education2)
    
    # 提交所有更改
    db.session.commit()
    
    print(f"✓ 创建用户: {user1.username}, {user2.username}")
    print(f"✓ 创建工作经历: {WorkExperience.query.count()} 条")
    print(f"✓ 创建教育背景: {EducationBackground.query.count()} 条")
    print(f"✓ 创建技能: {Skill.query.count()} 条")
    print(f"✓ 创建简历: {Resume.query.count()} 条")

def reset_database():
    """重置数据库"""
    with app.app_context():
        # 删除所有表
        db.drop_all()
        print("✓ 数据库表删除成功")
        
        # 重新创建表
        db.create_all()
        print("✓ 数据库表重新创建成功")
        
        # 创建示例数据
        create_sample_data()
        print("✓ 示例数据重新创建成功")

def show_database_info():
    """显示数据库信息"""
    with app.app_context():
        print("\n=== 数据库信息 ===")
        print(f"用户数量: {User.query.count()}")
        print(f"工作经历数量: {WorkExperience.query.count()}")
        print(f"教育背景数量: {EducationBackground.query.count()}")
        print(f"技能数量: {Skill.query.count()}")
        print(f"简历数量: {Resume.query.count()}")
        print(f"会话数量: {UserSession.query.count()}")
        
        print("\n=== 用户列表 ===")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} ({user.full_name}) - {user.email}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_database()
        elif command == 'reset':
            reset_database()
        elif command == 'info':
            show_database_info()
        else:
            print("可用命令: init, reset, info")
    else:
        init_database()
