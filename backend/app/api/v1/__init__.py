from fastapi import APIRouter
from app.api.v1 import auth, books, members, circulation, rfid, inventory, gates, migration, reports, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(books.router, prefix="/books", tags=["Books & Catalog"])
api_router.include_router(members.router, prefix="/members", tags=["Members"])
api_router.include_router(circulation.router, prefix="/circulation", tags=["Circulation"])
api_router.include_router(rfid.router, prefix="/rfid", tags=["RFID"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(gates.router, prefix="/gates", tags=["Security Gates"])
api_router.include_router(migration.router, prefix="/migration", tags=["Data Migration"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

