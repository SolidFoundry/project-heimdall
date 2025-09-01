#!/usr/bin/env python3
"""
检查数据库表结构
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from heimdall.core.config import get_config


async def check_schema():
    config = get_config()
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.database.user}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.name}"
    )

    async with engine.begin() as conn:
        # 检查user_behaviors表结构
        result = await conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'user_behaviors' 
            ORDER BY ordinal_position
        """
            )
        )

        print("user_behaviors表结构:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

        # 检查products表结构
        result = await conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            ORDER BY ordinal_position
        """
            )
        )

        print("\nproducts表结构:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_schema())
