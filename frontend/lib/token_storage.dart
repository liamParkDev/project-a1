import 'dart:html'; // ← web localStorage 사용

class TokenStorage {
  static const _access = 'access_token';
  static const _refresh = 'refresh_token';

  static Future<void> saveTokens(String access, String refresh) async {
    window.localStorage[_access] = access;
    window.localStorage[_refresh] = refresh;
  }

  static Future<String?> getAccess() async {
    return window.localStorage[_access];
  }

  static Future<String?> getRefresh() async {
    return window.localStorage[_refresh];
  }

  static Future<void> clear() async {
    window.localStorage.remove(_access);
    window.localStorage.remove(_refresh);
  }
}
