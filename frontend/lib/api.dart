import 'package:dio/dio.dart';
import 'token_storage.dart';

class Api {
  static final dio = Dio(BaseOptions(baseUrl: 'http://<너의-IP>:8000'));

  // 로그인
  static Future<bool> login(String email, String password) async {
    final res = await dio.post('/users/login', data: {
      "email": email,
      "password": password
    });

    final access = res.data["access_token"];
    final refresh = res.data["refresh_token"];

    await TokenStorage.saveTokens(access, refresh);
    return true;
  }

  // Access Token 자동 포함하여 API 호출
  static Future<Response> get(String path) async {
    final token = await TokenStorage.getAccess();
    return dio.get(
      path,
      options: Options(headers: {"Authorization": "Bearer $token"}),
    );
  }
}
