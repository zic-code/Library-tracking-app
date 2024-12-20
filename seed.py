# seed_data.py
from models import db, Stocks

def seed_data():
    stocks_data = [
        {'symbol': 'AAPL', 'sector': 'Technology (IT)', 'company_name': 'Apple'},
        {'symbol': 'MSFT', 'sector': 'Technology (IT)', 'company_name': 'Microsoft'},
        {'symbol': 'NVDA', 'sector': 'Technology (IT)', 'company_name': 'Nvidia'},
        {'symbol': 'GOOGL', 'sector': 'Technology (IT)', 'company_name': 'Alphabet'},
        {'symbol': 'AMZN', 'sector': 'Technology (IT)', 'company_name': 'Amazon'},
        
        {'symbol': 'MRNA', 'sector': 'Healthcare/Biotechnology', 'company_name': 'Moderna'},
        {'symbol': 'PFE', 'sector': 'Healthcare/Biotechnology', 'company_name': 'Pfizer'},
        {'symbol': 'GILD', 'sector': 'Healthcare/Biotechnology', 'company_name': 'Gilead Sciences'},
        {'symbol': 'REGN', 'sector': 'Healthcare/Biotechnology', 'company_name': 'Regeneron Pharmaceuticals'},
        {'symbol': 'VRTX', 'sector': 'Healthcare/Biotechnology', 'company_name': 'Vertex Pharmaceuticals'},
        
        {'symbol': 'TSLA', 'sector': 'Renewable Energy/Clean Energy', 'company_name': 'Tesla'},
        {'symbol': 'NEE', 'sector': 'Renewable Energy/Clean Energy', 'company_name': 'NextEra Energy'},
        {'symbol': 'ENPH', 'sector': 'Renewable Energy/Clean Energy', 'company_name': 'Enphase Energy'},
        {'symbol': 'BEP', 'sector': 'Renewable Energy/Clean Energy', 'company_name': 'Brookfield Renewable Partners'},
        {'symbol': 'FSLR', 'sector': 'Renewable Energy/Clean Energy', 'company_name': 'First Solar'},
        
        {'symbol': 'SHOP', 'sector': 'E-commerce', 'company_name': 'Shopify'},
        {'symbol': 'EBAY', 'sector': 'E-commerce', 'company_name': 'eBay'},
        {'symbol': 'ETSY', 'sector': 'E-commerce', 'company_name': 'Etsy'},
        {'symbol': 'MELI', 'sector': 'E-commerce', 'company_name': 'MercadoLibre'},
        {'symbol': 'BABA', 'sector': 'E-commerce', 'company_name': 'Alibaba'},
        
        {'symbol': 'PYPL', 'sector': 'Financial Technology (FinTech)', 'company_name': 'PayPal'},
        {'symbol': 'SQ', 'sector': 'Financial Technology (FinTech)', 'company_name': 'Square'},
        {'symbol': 'V', 'sector': 'Financial Technology (FinTech)', 'company_name': 'Visa'},
        {'symbol': 'MA', 'sector': 'Financial Technology (FinTech)', 'company_name': 'Mastercard'},
        {'symbol': 'COIN', 'sector': 'Financial Technology (FinTech)', 'company_name': 'Coinbase'}
    ]

    for stock in stocks_data:
        try:
            # 중복 확인
            existing_stock = Stocks.query.filter_by(symbol=stock["symbol"]).first()
            if existing_stock:
                print(f"Stock with symbol {stock['symbol']} already exists, skipping...")
                continue

            # 새 데이터 추가
            new_stock = Stocks(
                symbol=stock["symbol"],
                company_name=stock["company_name"],
                sector=stock["sector"]
            )
            db.session.add(new_stock)
            print(f"Added stock: {stock['symbol']}")  # 데이터 추가 메시지

        except Exception as e:
            # 오류 처리
            db.session.rollback()
            print(f"Error adding stock {stock['symbol']}: {e}")

    try:
        db.session.commit()
        print("All stock data inserted successfully!")  # 성공 메시지
    except Exception as e:
        db.session.rollback()
        print(f"Error during commit: {e}")

if __name__ == "__main__":
    seed_data()