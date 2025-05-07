from flask import Flask, render_template
import requests
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Đường dẫn API
GOLD_API_URL = "https://www.goldapi.io/api/XAU/USD?api_key=goldapi-aw2qg9smadshp6o-io"  # Dùng API key của bạn
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true"
CURRENCY_API_URL = "https://v6.exchangerate-api.com/v6/d8193d6ede36b4b8b827265b/latest/USD"

# Hàm lấy dữ liệu giá vàng
def get_gold_price():
    try:
        response = requests.get(GOLD_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Dữ liệu vàng:", data)  # In để kiểm tra
        if 'price' in data:
            return data['price']  # Giá vàng theo USD/ounce
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi lấy giá vàng: {e}")
        return None

# Tạo biểu đồ giá vàng
def create_gold_chart():
    years = [2019, 2020, 2021, 2022, 2023]
    gold_prices = [1500, 1700, 1800, 1900, 2000]  # Dữ liệu giả lập

    plt.figure(figsize=(8, 5))
    plt.plot(years, gold_prices, marker='o', color='gold')
    plt.title('Biểu đồ giá vàng theo năm')
    plt.xlabel('Năm')
    plt.ylabel('Giá vàng (USD/ounce)')
    plt.grid(True)

    # Đảm bảo thư mục static tồn tại
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Lưu biểu đồ
    chart_path = os.path.join(static_dir, 'gold_chart.png')
    plt.savefig(chart_path)
    plt.close()

@app.route('/')
def index():
    try:
        # Lấy dữ liệu từ API
        gold_price = get_gold_price()

        # Lấy dữ liệu thời tiết
        weather_response = requests.get(WEATHER_API_URL, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        print("Dữ liệu thời tiết:", weather_data)

        # Lấy dữ liệu tỷ giá
        currency_response = requests.get(CURRENCY_API_URL, timeout=10)
        currency_response.raise_for_status()
        currency_data = currency_response.json()
        print("Dữ liệu tỷ giá:", currency_data)

        # Tạo biểu đồ giá vàng
        create_gold_chart()

        # Chuẩn bị dữ liệu để hiển thị
        context = {
            'gold_price': gold_price if gold_price else 2300.50,  # Giá trị mặc định nếu API thất bại
            'weather_temp': weather_data.get('current', {}).get('temperature_2m', 25),  # Nhiệt độ mặc định 25°C
            'weather_code': weather_data.get('current', {}).get('weather_code', 0),  # Mã thời tiết mặc định 0
            'usd_to_vnd': currency_data.get('conversion_rates', {}).get('VND', 25000),  # Tỷ giá mặc định 25000
            'chart_image': 'gold_chart.png'  # Tên file biểu đồ
        }

        return render_template('index.html', **context)

    except requests.exceptions.RequestException as e:
        error_message = f"Lỗi khi lấy dữ liệu: {str(e)}"
        print("Lỗi:", error_message)
        return render_template('error.html', error=error_message), 500

if __name__ == '__main__':
    app.run(debug=True)