import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import Holdings, Transactions, get_db
from app.models.schemas import Holding, HoldingCreate, Transaction, TransactionCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("", response_model=list[Holding])
async def list_holdings(db: Session = Depends(get_db)):
    return db.query(Holdings).all()


@router.post("", response_model=Holding, status_code=201)
async def add_holding(holding: HoldingCreate, db: Session = Depends(get_db)):
    ticker = holding.ticker.upper()
    if db.query(Holdings).filter(Holdings.ticker == ticker).first():
        raise HTTPException(
            status_code=400,
            detail=f"Holding for {ticker} already exists. Delete it first to re-add.",
        )
    db_holding = Holdings(
        ticker=ticker,
        quantity=holding.quantity,
        avg_buy_price=holding.avg_buy_price,
    )
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding


@router.delete("/{ticker}")
async def delete_holding(ticker: str, db: Session = Depends(get_db)):
    holding = db.query(Holdings).filter(Holdings.ticker == ticker.upper()).first()
    if not holding:
        raise HTTPException(status_code=404, detail=f"Holding {ticker.upper()} not found")
    db.delete(holding)
    db.commit()
    return {"message": f"Deleted holding for {ticker.upper()}"}


@router.get("/transactions", response_model=list[Transaction])
async def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transactions).order_by(Transactions.date.desc()).all()


@router.post("/transactions", response_model=Transaction, status_code=201)
async def add_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    if tx.action not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="action must be 'buy' or 'sell'")
    db_tx = Transactions(
        ticker=tx.ticker.upper(),
        action=tx.action,
        quantity=tx.quantity,
        price=tx.price,
        notes=tx.notes,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx
