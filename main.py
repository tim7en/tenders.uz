from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import json

from database import get_db, User, Workspace
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    get_password_hash,
    get_user_by_username,
    get_user_by_email
)
from config import settings
import schemas

app = FastAPI(title="Tenders.uz API", description="A minimal app for user management and workspaces")

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/top-up-balance")
def top_up_balance(
    balance_data: schemas.BalanceTopUp,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if balance_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )
    
    current_user.balance += balance_data.amount
    db.commit()
    db.refresh(current_user)
    return {"message": f"Balance topped up by {balance_data.amount}", "new_balance": current_user.balance}

@app.put("/users/payment-info")
def update_payment_info(
    payment_data: schemas.PaymentInfoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate that payment_info is valid JSON
    try:
        json.loads(payment_data.payment_info)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Payment info must be valid JSON"
        )
    
    current_user.payment_info = payment_data.payment_info
    db.commit()
    db.refresh(current_user)
    return {"message": "Payment information updated successfully"}

@app.post("/workspaces", response_model=schemas.WorkspaceResponse)
def create_workspace(
    workspace: schemas.WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_workspace = Workspace(
        name=workspace.name,
        description=workspace.description,
        is_public=workspace.is_public,
        owner_id=current_user.id
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace

@app.get("/workspaces/my", response_model=list[schemas.WorkspaceResponse])
def get_my_workspaces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workspaces = db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()
    return workspaces

@app.get("/workspaces/public", response_model=list[schemas.WorkspaceResponse])
def get_public_workspaces(db: Session = Depends(get_db)):
    workspaces = db.query(Workspace).filter(Workspace.is_public == True).all()
    return workspaces

@app.get("/workspaces/{workspace_id}", response_model=schemas.WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )
    
    # Check if user can access this workspace (owner or public)
    if workspace.owner_id != current_user.id and not workspace.is_public:
        raise HTTPException(
            status_code=403,
            detail="Access denied to private workspace"
        )
    
    return workspace

@app.put("/workspaces/{workspace_id}", response_model=schemas.WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    workspace_data: schemas.WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )
    
    # Check if user owns this workspace
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only workspace owner can update"
        )
    
    # Update fields
    if workspace_data.name is not None:
        workspace.name = workspace_data.name
    if workspace_data.description is not None:
        workspace.description = workspace_data.description
    if workspace_data.is_public is not None:
        workspace.is_public = workspace_data.is_public
    
    db.commit()
    db.refresh(workspace)
    return workspace

@app.delete("/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )
    
    # Check if user owns this workspace
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only workspace owner can delete"
        )
    
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}

@app.get("/")
def root():
    return {"message": "Welcome to Tenders.uz API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)