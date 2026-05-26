from app.core.database import Base, engine
from app.models import User, TrackedProduct, PriceHistory, NotificationSettings, ScraperLog

target_metadata = Base.metadata

# No método run_migrations_online, altere connectable para:
connectable = engine