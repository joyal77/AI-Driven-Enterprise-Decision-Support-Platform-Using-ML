import sys
sys.path.append('backend')
from app.db.session import SessionLocal
from app.services.pdf_generator import generate_customer_prediction_pdf

db = SessionLocal()
buf = generate_customer_prediction_pdf(1, db)
db.close()
with open('customer_1_test.pdf', 'wb') as f:
    f.write(buf.getvalue())
print('PDF generated successfully, size:', len(buf.getvalue()))
