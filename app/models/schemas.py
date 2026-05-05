from datetime import datetime
from types import SimpleNamespace
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, PositiveInt, ValidationError, conint


class UserCreate(BaseModel):
    """Request body for creating a user account."""
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    """Response schema for user profile data."""
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload metadata."""
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None


class ProductOut(BaseModel):
    """Product data returned from listing endpoints."""
    id: int
    name: str
    description: str
    category: str
    price: float
    stock_qty: int = Field(..., ge=0)
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class ProductListResponse(BaseModel):
    """Paged response for product listings."""
    items: List[ProductOut]
    page: PositiveInt
    page_size: PositiveInt
    total: int = Field(..., ge=0)


class OrderOut(BaseModel):
    """Order representation with nested product data."""
    id: int
    user_id: int
    product_id: int
    quantity: PositiveInt
    unit_price: float
    total_price: float
    order_status: str
    created_at: datetime
    product: ProductOut

    class Config:
        orm_mode = True


class DashboardSummary(BaseModel):
    """Dashboard KPI summary for a user."""
    total_products: int = Field(..., ge=0)
    total_orders: int = Field(..., ge=0)
    pending_orders: int = Field(..., ge=0)
    shipped_orders: int = Field(..., ge=0)
    total_spent: float


def test_usercreate_validation() -> None:
    """Prevent invalid email or short password from being accepted."""
    invalid_inputs = [
        {"name": "Tester", "email": "not-an-email", "password": "longpass"},
        {"name": "Tester", "email": "tester@example.com", "password": "short"},
    ]
    for kwargs in invalid_inputs:
        try:
            UserCreate(**kwargs)
        except ValidationError:
            continue
        raise AssertionError("UserCreate accepted invalid input")


def test_productout_serialization() -> None:
    """Ensure ProductOut can be created from an ORM-like object."""
    source = SimpleNamespace(
        id=1,
        name="Widget",
        description="A widget",
        category="gadgets",
        price=25.0,
        stock_qty=10,
        image_url="https://example.com/widget.png",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    product = ProductOut.from_orm(source)
    assert product.name == source.name


def test_orderout_nested_product() -> None:
    """Verify OrderOut serializes nested ProductOut data."""
    product = ProductOut(
        id=2,
        name="Gadget",
        description="A gadget",
        category="tools",
        price=15.0,
        stock_qty=5,
        created_at=datetime(2025, 1, 2, 12, 0, 0),
    )
    order = OrderOut(
        id=1,
        user_id=10,
        product_id=product.id,
        quantity=1,
        unit_price=product.price,
        total_price=product.price,
        order_status="pending",
        created_at=datetime(2025, 1, 3, 12, 0, 0),
        product=product,
    )
    serialized = order.dict()
    assert serialized["product"]["id"] == product.id
