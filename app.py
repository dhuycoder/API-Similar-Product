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
try:
   
    print("✅ Kết nối MySQL thành công!")
    query = "Select * from product"
    df_sanphams = pd.read_sql(query,engine)
    print(df_sanphams.head())
   

except Exception as e:
    print(f"❌ Lỗi kết nối: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("🔌 Đã đóng kết nối.")

features = ['description','price']

def combineFeatures(row):
    return  str(row['description'])

df_sanphams['combinedFeatures'] = df_sanphams.apply(combineFeatures,axis = 1)
print(df_sanphams['combinedFeatures'])

tf = TfidfVectorizer()
tfMatrix = tf.fit_transform(df_sanphams['combinedFeatures'])

similar = cosine_similarity(tfMatrix)


number = 5
@app.route('/api',methods=['Get'])
def get_data():
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
        return (df_sanphams[df_sanphams.index == index]['name'].values[0])

    for i in range(1,number + 1):
        print(lay_ten(sortedSimilarProduct[i][0]))
        ket_qua.append(lay_ten(sortedSimilarProduct[i][0]))


    data = {'san pham goi y: ':ket_qua}
   
    return jsonify(data)

if __name__ == '__main__':
    app.run(port = 5555)