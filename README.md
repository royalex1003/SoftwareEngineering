## SoftwareEngineering 2023

## Coin Market
## Flask, sqlalchemy

### 주요 기능들

### 회원가입
#### 1) 사용자는 웹 브라우저를 통해 회원 가입이 가능하며 자신의 계정을 생성시 보유 금액과 코인은 0으로 고정한다.
#### 2) 회원 가입시 SQLAlchemy에 USER Table에 저장된다.


### 로그인 상태
#### 1) USER Table에 저장된 ID와 PW를 통해 로그인이 이루어진다.
#### 2) Session을 통해 로그인 상태를 확인하며 로그아웃 기능으로 세션에서 벗어난다.
#### 3) 로그인 또는 로그 아웃 상태에서도 동일한 기능이 요구가 되므로 main 화면을 2개로 구성하였다.
#### 4) 사용자는 코인을 업로드 할 수 있으며 본인이 업로드 한 코인은 구매가 불가하다. 또한 보유 금액이 코인의 가격보다 적은 경우에도 코인을 구매 할 수 없다. 
#### 5) 사용자는 입/출금 기능을 통해 보유 금액을 원하는 액수만큼 지정할 수 있다.


### 로그인 또는 로그 아웃 상태
#### 1) 코인 거래시 코인의 정보를 담고 있는 게시판이 업데이트 된다.
#### 2)현재 코인 가격 및 가격 동향(그래프)을 거래 시각과 당시 코인 가격으로 확인할 수 있다.

