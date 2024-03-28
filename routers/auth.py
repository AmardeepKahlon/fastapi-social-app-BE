from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Union, cast

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing_extensions import Annotated, Doc  # typ
from config import models
from config.models import User
from config.schemas import Login, UserCreate
from config.database import get_db
from lib.token import create_access_token
from lib.hash import Hash

router = APIRouter(
  tags=["Authentication"]
)

revoked_tokens = set()
class OAuth2PasswordRequestForm:
    """
    This is a dependency class to collect the `username` and `password` as form data
    for an OAuth2 password flow.

    The OAuth2 specification dictates that for a password flow the data should be
    collected using form data (instead of JSON) and that it should have the specific
    fields `username` and `password`.

    All the initialization parameters are extracted from the request.

    Read more about it in the
    [FastAPI docs for Simple OAuth2 with Password and Bearer](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/).

    ## Example

    ```python
    from typing import Annotated

    from fastapi import Depends, FastAPI
    from fastapi.security import OAuth2PasswordRequestForm

    app = FastAPI()


    @app.post("/login")
    def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        data = {}
        data["scopes"] = []
        for scope in form_data.scopes:
            data["scopes"].append(scope)
        if form_data.client_id:
            data["client_id"] = form_data.client_id
        if form_data.client_secret:
            data["client_secret"] = form_data.client_secret
        return data
    ```

    Note that for OAuth2 the scope `items:read` is a single scope in an opaque string.
    You could have custom internal logic to separate it by colon caracters (`:`) or
    similar, and get the two parts `items` and `read`. Many applications do that to
    group and organize permisions, you could do it as well in your application, just
    know that that it is application specific, it's not part of the specification.
    """

    def __init__(
        self,
        *,
        grant_type: Annotated[
            Union[str, None],
            Form(pattern="password"),
            Doc(
                """
                The OAuth2 spec says it is required and MUST be the fixed string
                "password". Nevertheless, this dependency class is permissive and
                allows not passing it. If you want to enforce it, use instead the
                `OAuth2PasswordRequestFormStrict` dependency.
                """
            ),
        ] = None,
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                `username` string. The OAuth2 spec requires the exact field name
                `username`.
                """
            ),
        ],
        # password: Annotated[
        #     str,
        #     Form(),
        #     Doc(
        #         """
        #         `password` string. The OAuth2 spec requires the exact field name
        #         `password".
        #         """
        #     ),
        # ],
        scope: Annotated[
            str,
            Form(),
            Doc(
                """
                A single string with actually several scopes separated by spaces. Each
                scope is also a string.

                For example, a single string with:

                ```python
                "items:read items:write users:read profile openid"
                ````

                would represent the scopes:

                * `items:read`
                * `items:write`
                * `users:read`
                * `profile`
                * `openid`
                """
            ),
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form(),
            Doc(
                """
                If there's a `client_id`, it can be sent as part of the form fields.
                But the OAuth2 specification recommends sending the `client_id` and
                `client_secret` (if any) using HTTP Basic auth.
                """
            ),
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form(),
            Doc(
                """
                If there's a `client_password` (and a `client_id`), they can be sent
                as part of the form fields. But the OAuth2 specification recommends
                sending the `client_id` and `client_secret` (if any) using HTTP Basic
                auth.
                """
            ),
        ] = None,
    ):
        self.grant_type = grant_type
        self.username = username
        # self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

# Register user API endpoint
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # print(user.email.name)
    if not user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
    if not user.name or user.name == "":
        user.name = user.email.name
    elif not user.name.strip() or user.name.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name")

    if (
        user_exists := db.query(models.User)
        .filter(models.User.email == user.email.email)
        .first()
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user = models.User(email=user.email.email, name=user.name)
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}

# Login user API endpoint
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = db.query(User).filter(User.email == request.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
  # if not Hash.verify(user.password, request.password):
  #   raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")
  access_token = create_access_token(
    data = {"sub": user.email, "id": user.id, "name": user.name}
  )
  return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_name": user.name,
    "user_id": user.id
  }
  
# Logout user API endpoint
@router.post("/logout")
def logout(access_token: str, db: Session = Depends(get_db)):
    if access_token in revoked_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already revoked")
    revoked_tokens.add(access_token)
    return {"message": "Logout successful"}