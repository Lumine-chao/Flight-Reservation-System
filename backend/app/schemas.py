from typing import Optional

from pydantic import BaseModel


class RegisterIn(BaseModel):
    username: str
    password: str
    confirmPassword: str
    securityQuestion: str
    securityAnswer: str


class LoginIn(BaseModel):
    username: str
    password: str


class SecurityQuestionIn(BaseModel):
    username: str


class ResetPasswordIn(BaseModel):
    username: str
    securityAnswer: str
    newPassword: str


class OrderCreateIn(BaseModel):
    flightNo: str
    flightDate: str
    fromCity: str
    toCity: str
    passengerName: str
    ticketCount: int = 1
    seatClass: str = "ECONOMY"


class OrderUpdateIn(BaseModel):
    # orderNo 出现在请求体中视为非法修改（3006）
    orderNo: Optional[str] = None
    flightNo: Optional[str] = None
    flightDate: Optional[str] = None
    fromCity: Optional[str] = None
    toCity: Optional[str] = None
    passengerName: Optional[str] = None
    ticketCount: Optional[int] = None
    seatClass: Optional[str] = None


class CityCreateIn(BaseModel):
    cityCode: str
    cityName: str
    province: Optional[str] = ""


class CityStatusIn(BaseModel):
    status: int


class FlightUpsertIn(BaseModel):
    id: Optional[int] = None
    flightNo: str
    fromCity: str
    toCity: str
    departTime: str
    arriveTime: str
    airline: str
    priceEconomy: float
    priceBusiness: float
    priceFirst: float
    seatRemain: int = 100
    status: int = 1


class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminHandleIn(BaseModel):
    action: str = "cancel"
    remark: Optional[str] = None
