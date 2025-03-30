import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify, request
app = Flask(__name__)
# Thông tin MySQL
server = '127.0.0.1'
database = 'chronoluxweb'
username = 'root'
password = '12345678'
engine = create_engine(f"mysql+pymysql://{username}:{password}@{server}/{database}")
# Kết nối MySQL
features = ['description','price']

def combineFeatures(row):
    return str(row['description']) + " " + str(row['name'])

def kiem_tra_ton_kho(product_id):
    """
    Kiểm tra sản phẩm có còn hàng hay không.
    Trả về True nếu instock > 0, ngược lại trả về False.
    """
    query = f"SELECT instock FROM product WHERE id = {product_id} LIMIT 1"
    df = pd.read_sql(query, engine)
    print("query:",query)
    if not df.empty and df.iloc[0]['instock'] > 0:
    
        return True
    return False

number = 5
@app.route('/api',methods=['Get'])
def get_data():
    try:
    
        print("✅ Kết nối MySQL thành công!")
        query = "SELECT * FROM product"
        df_sanphams = pd.read_sql(query,engine)
        print(df_sanphams.head())
    

    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()
            print("🔌 Đã đóng kết nối.")
    
    df_sanphams['combinedFeatures'] = df_sanphams.apply(combineFeatures,axis = 1)
    print(df_sanphams['combinedFeatures'])

    tf = TfidfVectorizer()
    tfMatrix = tf.fit_transform(df_sanphams['combinedFeatures'])

    similar = cosine_similarity(tfMatrix)
    
    ket_qua = []
    productid = request.args.get('id')

    productid = int(productid)
    
      
    if productid not in df_sanphams['id'].values:
       
        return jsonify({'loi': 'khong tim thay id'})

    indexProduct = df_sanphams[df_sanphams['id'] == productid].index[0]
    similarProduct =list(enumerate(similar[indexProduct]))
    print (similarProduct)
    sortedSimilarProduct = sorted(similarProduct,key=lambda x:x[1],reverse=True)

    def lay_ten(index):
            # Lọc sản phẩm dựa trên cột 'id' chứ không phải index
        filtered_df = df_sanphams[df_sanphams['id'] == product_id]
        
       

        # Kiểm tra nếu có sản phẩm được tìm thấy
        if not filtered_df.empty:
            return filtered_df['name'].values[0]  # Lấy tên sản phẩm đầu tiên
        else:
            return "Không tìm thấy sản phẩm!"

   
    
    # Kiểm tra xem sản phẩm có tồn kho không
    so_luong_can_lay = 5  # Số lượng sản phẩm cần lấy
  
    i = 1  # Bắt đầu từ sản phẩm đầu tiên
    so_san_pham = len(sortedSimilarProduct)  # Tổng số sản phẩm trong danh sách

    while len(ket_qua) < so_luong_can_lay and i < so_san_pham:
        product_id = sortedSimilarProduct[i][0]

        if kiem_tra_ton_kho(product_id):  # Kiểm tra instock
            print("product id:",product_id)
            ten_san_pham = lay_ten(product_id)
            print(ten_san_pham)
            ket_qua.append(ten_san_pham)

        i += 1  # Tiếp tục kiểm tra sản phẩm tiếp theo


    data = {'san pham goi y: ':ket_qua}
   
    return jsonify(data)

if __name__ == '__main__':
    app.run(port = 5555)