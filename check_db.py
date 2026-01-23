"""
Check if push_subscriptions table exists
"""
from app.database.connection import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)

for table in sorted(tables):
    print(f"  ✓ {table}")

print("\n" + "=" * 60)

if "push_subscriptions" in tables:
    print("✅ push_subscriptions table EXISTS")
    
    # Get columns
    columns = inspector.get_columns("push_subscriptions")
    print("\nColumns:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
else:
    print("❌ push_subscriptions table MISSING!")
    print("\nTo fix, run:")
    print("  alembic upgrade head")

print("=" * 60)
