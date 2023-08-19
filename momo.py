from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
import re
import pandas as pd
from sqlalchemy import create_engine

def main():
# Flask code

    app = Flask(__name__)

    # Connecting to MySQL database
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = '3306'  # MySQL default port
    MYSQL_DATABASE = 'products'

    # Configure SQLAlchemy for MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    db = SQLAlchemy(app)

    class Product(db.Model):
        __tablename__ = 'product'
        id = db.Column(db.Integer, primary_key=True)
        Product_Pic = db.Column(db.String(200),nullable=True)
        Product_Name = db.Column(db.String(200),nullable=True)
        Price = db.Column(db.String(100),nullable=True)
        Sales = db.Column(db.String(100),nullable=True)
        Slogan = db.Column(db.String(100),nullable=True)
        Link = db.Column(db.String(200),nullable=True)
        Product_Brand = db.Column(db.String(100),nullable=True)
        Product_Price = db.Column(db.Integer,nullable=True)
        Product_Sales = db.Column(db.Integer,nullable=True)

        def __repr__(self):
            return f"<Product(Product_Name={self.Product_Name}, Price={self.Price}, Sales={self.Sales}, ...)>"

    
    @app.route('/result')
    def result():
        prods = Product.query.all()
        prods_sorted = sorted(prods, key=lambda prod: prod.Product_Sales, reverse=True)
        return render_template('result.html', prods=prods_sorted)


    @app.route('/',methods = ['GET','POST'])
    def index():
        if request.method == 'POST':
            keyword = request.form.get('keyword')  # Get the keyword from the form
            try:
                message = scrape_and_store_data(keyword)  # Call the scraping function
                if message == "Scraping and storing done.":
                    return redirect(url_for('result'))
                return render_template('index.html', message=message)
            except Exception:
                return render_template('error.html')

        return render_template('index.html')

    if __name__ == "__main__":
        app.run(debug=True)





def scrape_and_store_data(word):
    
    url = "https://www.momoshop.com.tw/search/searchShop.jsp?keyword=" + word
    # headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}

    browser = webdriver.Chrome()
    browser.maximize_window()

    print('搜尋\'{}\''.format(word))
    print('-------------------------------------------------')
    browser.get(url)

    # 等到 menuArea 欄位出現並繼續
    WebDriverWait(browser,20).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME,'menuArea')))

    # 尋找‘月銷量’欄位並點選
    option = browser.find_element(By.CLASS_NAME, "popularPrd")
    option.click()

    # 截取網頁資料
    soup = bs(browser.page_source,'html.parser')


    #%% 尋找‘月銷量’商品數量頁面
    b=[]
    a=soup.select('dt span')
    for c in a:
        b.append(c.text)
        
    text = b[1]
    pattern = r"/(\d+)$"
    match = re.search(pattern, text)
    if match:
        page_count = match.group(1)
        print("總共 {} 頁".format(page_count)) 

    #%% 尋找網頁基本鏈接
    url = browser.current_url
    url_root = url.replace("&_isFuzzy=0&showType=chessboardType&isBrandCategory=N&serviceCode=MT01","")

    while url_root[-1]!="=":
        url_root = url_root.replace(url_root[-1],"")
    # print(url_root)

    #%% 以 looping 爬取所有頁面資料 --default 示範設定為 5
    
    prd_image_link = []
    prd_link = []
    prd_slogan = []
    prd_name = []
    prd_price = []
    prd_sales = []

    if int(page_count)<5:
        page_num = int(page_count)
    else:
        page_num = 1

    # for i in range(int(page_count)):
    for i in range(page_num):
        print("Scraping details from page",i+1)
        url_new = url_root + str(i+1)
        
        browser.get(url_new)

        WebDriverWait(browser,10).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME,'menuArea')))
        
        soup = bs(browser.page_source,'html.parser')

        product_pic = soup.find_all('div', class_='swiper-slide swiper-slide-active')
        for pic in product_pic:
            img_tag=pic.find('img')
            src_value = img_tag['src']
            prd_image_link.append(src_value)

        product_link = soup.find_all('a',class_='goodsUrl')
        for link in product_link:
            prd_link.append("https://www.momoshop.com.tw/" + link.get('href'))
            
        product_slogan = soup.select('p.sloganTitle')
        for ps in product_slogan:
            prd_slogan.append(ps.text)
            
        product_name = soup.select('h3.prdName')
        for pn in product_name:
            prd_name.append(pn.text)
                
        product_price = soup.select('span.price')
        for pp in product_price:
            prd_price.append(pp.text)
            
        product_sales = soup.select('span.totalSales.goodsTotalSales')
        for psales in product_sales:
            prd_sales.append(psales.text)

    data = {'Product_Pic': prd_image_link,
            'Product_Name': prd_name,
            'Price': prd_price,
            'Sales': prd_sales,
            'Slogan': prd_slogan,
            'Link': prd_link}

    browser.close()

    # 建立 DataFrame 並存取資料進入 csv 檔案 raw data
    word_split = word.split()
    filename = ''
    if len(word_split) > 1:
        for i in range(len(word_split)):
            filename += (word_split[0] + '_')
    else:
        filename = word

    print("Saving data into csv...")
    df = pd.DataFrame(data)
    df.to_csv('{}商品資料.csv'.format(filename),encoding = 'utf-8',index=False, header=True)

    #%%
    #—————————————————————————————————————————————————————————————————
    #                         數據處理
    #—————————————————————————————————————————————————————————————————

    #讀取csv檔案
    print("Opening csv file for data processing...")
    df = pd.read_csv(filename+'商品資料.csv')
    # print(df.info())


    # 資料處理

    # 找出品牌名稱並存在一個新的欄位
    df['Product_Brand'] = df['Product_Name'].str.extract('\【(.*)\】')
    ItemsbyBrand=df.groupby(['Product_Brand']).count()

    #%%
    # 處理價格格式從 $12，999 => 12999 並存在一個新的欄位
    # print(df.Price.head(20))
    df['Product_Price'] = df.Price.str.replace(',','')
    df['Product_Price'] = df['Product_Price'].apply(lambda x: int(x[1:]) if x[-1]>='0'and x[-1]<='9' else None)
    # print(df['Product_Price'].head(20))

    #%%
    # 處理銷量格式 總銷量>1,000 => 1000， 總銷量>1.5萬 => 15000 並存在一個新的欄位
    # print(df.Sales.head(30))
    df['Product_Sales'] = df.Sales.str.extract('\>(.*)')
    df['Product_Sales'] = df.Product_Sales.str.replace(',','')
    # print(df.Product_Sales.head(30))

    # Multiply values with '萬' by 10,000
    df['Product_Sales'] = df['Product_Sales'].apply(lambda x: 
                                                    float(str(x).replace('萬', '')) * 10000 
                                                    if isinstance(x, str) and '萬' in x else x)
    # Convert all to numeric values
    df['Product_Sales'] = pd.to_numeric(df['Product_Sales'], errors='coerce')
    # Convert remaining values to integers
    df['Product_Sales'] = df['Product_Sales'].astype('Int64')
    # print(df['Product_Sales'].head(30))
    df.drop(['Sales'],axis=1)

    #Sort according to brand and sales
    df_sorted = df.sort_values(by=['Product_Brand','Product_Sales'],ascending = False)
    df_sorted.insert(0, 'id', range(1, 1 + len(df_sorted)))
    df_sorted.fillna(0,inplace=True)
    df_sorted.to_csv('{}商品資料sorted.csv'.format(filename),encoding = 'utf-8',index=False, header=True)
    
    #%%
    #—————————————————————————————————————————————————————————————————
    #                         存入Mysql 資料庫
    #—————————————————————————————————————————————————————————————————

    username = 'root'
    password = ''
    host = 'localhost:3306'  
    database_name = 'products'

    # 鏈接資料庫 Create a database connection URL
    db_url = f'mysql+pymysql://{username}:{password}@{host}/{database_name}'

    # Create a database engine
    engine = create_engine(db_url)

    df = pd.read_csv('{}商品資料sorted.csv'.format(filename))

    table_name = 'product'

    # 上傳資料到Mysql資料庫 Upload the DataFrame to MySQL
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    return "Scraping and storing done."

main()
