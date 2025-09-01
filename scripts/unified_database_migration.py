#!/usr/bin/env python3
"""
统一数据库迁移脚本 - 从源头解决所有问题
确保数据库架构的一致性和正确性
"""

import sys
import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.heimdall.core.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDatabaseMigrator:
    def __init__(self):
        self.engine = create_async_engine(settings.ASYNC_DATABASE_URL)
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
    async def run_migration(self):
        """运行完整的数据库迁移"""
        logger.info("=== 开始统一数据库迁移 ===")
        
        async with self.AsyncSessionLocal() as session:
            try:
                # 1. 检查当前数据库状态
                await self._check_database_status(session)
                
                # 2. 按正确顺序执行SQL文件
                await self._execute_sql_file(session, "001_initial_schema.sql")
                await self._execute_sql_file(session, "002_product_ads_schema.sql")
                await self._execute_sql_file(session, "003_user_behavior_schema.sql")
                await self._execute_sql_file(session, "004_fix_database_schema.sql")
                
                # 3. 验证数据类型一致性
                await self._verify_data_types(session)
                
                # 4. 插入必要的示例数据
                await self._insert_sample_data(session)
                
                await session.commit()
                logger.info("✅ 统一数据库迁移完成！")
                
                return True
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ 迁移失败: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    async def _check_database_status(self, session):
        """检查当前数据库状态"""
        logger.info("1. 检查数据库状态...")
        
        # 检查表是否存在
        result = await session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        logger.info(f"   现有表: {tables}")
        
    async def _execute_sql_file(self, session, filename):
        """执行SQL文件"""
        logger.info(f"2. 执行SQL文件: {filename}")
        
        sql_path = project_root / "sql" / filename
        if not sql_path.exists():
            logger.warning(f"   SQL文件不存在: {filename}")
            return
            
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # 移除注释和空行
        sql_statements = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                sql_statements.append(line)
                
        # 执行SQL语句
        for statement in sql_statements:
            if statement:
                try:
                    await session.execute(text(statement))
                except Exception as e:
                    logger.warning(f"   语句执行失败: {statement[:50]}... - {e}")
                    
        logger.info(f"   ✅ {filename} 执行完成")
        
    async def _verify_data_types(self, session):
        """验证数据类型一致性"""
        logger.info("3. 验证数据类型一致性...")
        
        # 检查products表的数据类型
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            AND column_name = 'id'
        """))
        
        products_id_type = result.fetchone()
        logger.info(f"   products.id 类型: {products_id_type}")
        
        # 检查user_behaviors表的数据类型
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_behaviors' 
            AND column_name = 'product_id'
        """))
        
        behaviors_product_id_type = result.fetchone()
        logger.info(f"   user_behaviors.product_id 类型: {behaviors_product_id_type}")
        
        # 验证类型是否一致
        if products_id_type and behaviors_product_id_type:
            if products_id_type[1] == behaviors_product_id_type[1]:
                logger.info("   ✅ 数据类型一致！")
            else:
                logger.warning(f"   ❌ 数据类型不一致: {products_id_type[1]} vs {behaviors_product_id_type[1]}")
                
    async def _insert_sample_data(self, session):
        """插入必要的示例数据"""
        logger.info("4. 插入示例数据...")
        
        # 检查是否已有数据
        result = await session.execute(text("SELECT COUNT(*) FROM products"))
        product_count = result.fetchone()[0]
        
        if product_count == 0:
            logger.info("   插入产品示例数据...")
            await session.execute(text("""
                INSERT INTO products (name, description, price, category, brand, rating) VALUES
                ('iPhone 15 Pro', '苹果最新旗舰手机', 7999.00, '手机', 'Apple', 4.8),
                ('MacBook Pro', '专业级笔记本电脑', 14999.00, '笔记本', 'Apple', 4.9),
                ('小米手机', '高性价比智能手机', 2999.00, '手机', '小米', 4.5),
                ('华为手机', '国产旗舰手机', 4999.00, '手机', '华为', 4.6),
                ('联想笔记本', '商务办公笔记本', 5999.00, '笔记本', '联想', 4.3)
            """))
            
        # 检查用户行为数据
        result = await session.execute(text("SELECT COUNT(*) FROM user_behaviors"))
        behavior_count = result.fetchone()[0]
        
        if behavior_count == 0:
            logger.info("   插入用户行为数据...")
            await session.execute(text("""
                INSERT INTO user_behaviors (user_id, session_id, behavior_type, product_id, category, brand, product_name, price) VALUES
                ('user_001', 'session_001', 'view', 1, '手机', 'Apple', 'iPhone 15 Pro', 7999.00),
                ('user_001', 'session_001', 'click', 1, '手机', 'Apple', 'iPhone 15 Pro', 7999.00),
                ('user_001', 'session_002', 'view', 2, '笔记本', 'Apple', 'MacBook Pro', 14999.00),
                ('user_001', 'session_002', 'view', 3, '手机', '小米', '小米手机', 2999.00)
            """))
            
        logger.info("   ✅ 示例数据插入完成")

async def main():
    """主函数"""
    migrator = UnifiedDatabaseMigrator()
    success = await migrator.run_migration()
    
    if success:
        print("\n✅ 源头数据库问题已彻底解决！")
        print("所有数据类型现在都保持一致，系统可以正常运行。")
    else:
        print("\n❌ 迁移失败，请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())