import 'package:dio/dio.dart';
import 'token_storage.dart';

class Api {
  static final dio = Dio(
    BaseOptions(
      baseUrl: 'http://app.local',  // <-- 너의 IP 또는 도메인
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
      headers: {
        'Content-Type': 'application/json',
      },
    ),
  );

  // --------------------
  // 로그인 (access + refresh 저장)
  // --------------------
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

  // --------------------
  // Authorization 자동 포함된 GET 요청
  // --------------------
  static Future<Response> get(String path) async {
    final token = await TokenStorage.getAccess();

    if (token == null) {
      throw Exception("Access Token 없음! 다시 로그인 필요");
    }

    return dio.get(
      path,
      options: Options(
        headers: {"Authorization": "Bearer $token"},
      ),
    );
  }

  static Future<Response> post(String path, Map<String, dynamic> data) async {
    final token = await TokenStorage.getAccess();

    return dio.post(
      path,
      data: data,
      options: Options(
        headers: {"Authorization": "Bearer $token"},
      ),
    );
  }
}
