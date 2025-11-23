import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static const _access = 'access_token';
  static const _refresh = 'refresh_token';

  static const storage = FlutterSecureStorage();

  static Future<void> saveTokens(String access, String refresh) async {
    await storage.write(key: _access, value: access);
    await storage.write(key: _refresh, value: refresh);
  }

  static Future<String?> getAccess() async {
    return await storage.read(key: _access);
  }

  static Future<String?> getRefresh() async {
    return await storage.read(key: _refresh);
  }

  static Future<void> clear() async {
    await storage.deleteAll();
  }
}
