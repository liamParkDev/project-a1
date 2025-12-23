import 'package:dio/dio.dart';
import 'token_storage.dart';

class Api {
  static final dio = Dio(
    BaseOptions(
      baseUrl: 'http://app.local/api',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
      headers: {'Content-Type': 'application/json'},
    ),
  )..interceptors.add(_AuthInterceptor()); // 인터셉터 추가

  static Future<Response> get(String path) async {
    return dio.get(path);
  }

  static Future<Response> post(String path, Map<String, dynamic> data) async {
    return dio.post(path, data: data);
  }

  static Future<bool> register(String email, String password, String nickname) async {
    final res = await dio.post('/users/register', data: {
      "email": email,
      "password": password,
      "nickname": nickname,
    });

    final access = res.data["access_token"];
    final refresh = res.data["refresh_token"];
    if (access != null && refresh != null) {
      await TokenStorage.saveTokens(access, refresh);
    }
    return true;
  }

  static Future<bool> login(String email, String password) async {
    final res = await dio.post('/users/login', data: {
      "email": email,
      "password": password,
    });

    final access = res.data["access_token"];
    final refresh = res.data["refresh_token"];

    await TokenStorage.saveTokens(access, refresh);
    return true;
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final access = await TokenStorage.getAccess();
    if (access != null) {
      options.headers['Authorization'] = 'Bearer $access';
    }
    super.onRequest(options, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Access Token 만료 → 401 발생
    if (err.response?.statusCode == 401) {
      print(" Access Token 만료 → Refresh Token으로 재발급 시도");

      final refreshed = await _refreshTokens();
      if (refreshed) {
        final RequestOptions req = err.requestOptions;
        final newAccess = await TokenStorage.getAccess();

        req.headers['Authorization'] = 'Bearer $newAccess';

        final cloned = await Api.dio.fetch(req);
        return handler.resolve(cloned);
      } else {
        print(" Refresh Token도 만료 → 자동 로그아웃");
        await TokenStorage.clear();
        return handler.next(err);
      }
    }

    return handler.next(err);
  }

  Future<bool> _refreshTokens() async {
    final refresh = await TokenStorage.getRefresh();
    if (refresh == null) return false;

    try {
      final res = await Api.dio.post('/users/refresh', data: {
        "refresh_token": refresh,
      });

      final newAccess = res.data["access_token"];
      // refresh 응답이 access만 내려오므로 refresh 토큰은 기존 값 유지
      final newRefresh = res.data["refresh_token"] ?? refresh;

      await TokenStorage.saveTokens(newAccess, newRefresh);
      print(" Token 재발급 성공");

      return true;
    } catch (e) {
      print(" Refresh Token 재발급 실패: $e");
      return false;
    }
  }
}
