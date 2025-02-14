##### Building a Docker Image
```
docker build -t my-docker-image .
```
<br>

##### Running a Docker Container
```
docker run -d --name my-docker-container -p 8000:8000 -v .:/app my-docker-image
```
<br>

##### Running a Docker Container from a Docker Compose file
```
docker compose up -d
```

<br>

##### Build the images without using the cache
```
docker-compose build --no-cache
```

##### VNpay Dashboard test
```
https://sandbox.vnpayment.vn/merchantv2/Home/Dashboard.htm
```

##### Card test
```
Ngân hàng	NCB
Số thẻ	9704198526191432198
Tên chủ thẻ	NGUYEN VAN A
Ngày phát hành	07/15
Mật khẩu OTP	123456
```