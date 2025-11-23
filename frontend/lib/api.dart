import 'package:dio/dio.dart';
import 'token_storage.dart';

class Api {
  static final dio = Dio(
    BaseOptions(
      baseUrl: 'http://app.local/api',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
      headers: {
        'Content-Type': 'application/json',
      },
    ),
  );

  static Future<bool> login(String email, String password) async {
    try {
      final res = await dio.post('/users/login', data: {
        "email": email,
        "password": password,
      });

      final access = res.data["access_token"];
      final refresh = res.data["refresh_token"];

      if (access == null || refresh == null) {
        throw Exception("토큰이 없습니다!");
      }

      await TokenStorage.saveTokens(access, refresh);
      return true;

    } catch (e) {
      print("로그인 실패: $e");
      rethrow;
    }
  }

  static Future<Response> get(String path) async {
    final token = await TokenStorage.getAccess();
    if (token == null) throw Exception("Access Token 없음!");

    return dio.get(
      path,
      options: Options(headers: {"Authorization": "Bearer $token"}),
    );
  }

  static Future<Response> post(String path, Map<String, dynamic> data) async {
    final token = await TokenStorage.getAccess();
    if (token == null) throw Exception("Access Token 없음!");

    return dio.post(
      path,
      data: data,
      options: Options(headers: {"Authorization": "Bearer $token"}),
    );
  }
}
