"""
Manually create push_subscriptions table if migration doesn't work
"""
from app.database.connection import engine
from sqlalchemy import text

create_table_sql = """
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR NOT NULL,
    p256dh VARCHAR NOT NULL,
    auth VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_user_endpoint UNIQUE (user_id, endpoint)
);

CREATE INDEX IF NOT EXISTS ix_push_subscriptions_id ON push_subscriptions(id);
"""

print("Creating push_subscriptions table...")

try:
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("✅ Table created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
