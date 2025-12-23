import 'package:flutter/material.dart';
import 'api.dart';
import 'token_storage.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final pwController = TextEditingController();
  final nicknameController = TextEditingController();

  bool loading = false;
  String? errorMessage;
  bool isLogin = true;

  Future<void> _submit() async {
    setState(() {
      loading = true;
      errorMessage = null;
    });

    try {
      final email = emailController.text.trim();
      final password = pwController.text.trim();
      final nickname = nicknameController.text.trim();

      final ok = isLogin
          ? await Api.login(email, password)
          : await Api.register(email, password, nickname);

      if (ok && mounted) {
        // 성공 → 홈으로 이동
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      setState(() {
        errorMessage = "실패: ${e.toString()}";
      });
    }

    setState(() {
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SizedBox(
          width: 350,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // ---- 이미지 로고 ----
              Image.asset(
                "assets/logo.png",
                height: 120,
              ),
              const SizedBox(height: 30),

              Text(
                isLogin ? "Project A1 Login" : "Project A1 회원가입",
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 30),

              // --- Email ---
              TextField(
                controller: emailController,
                decoration: const InputDecoration(
                  labelText: "Email",
                  border: OutlineInputBorder(),
                ),
              ),

              const SizedBox(height: 15),

              // --- Password ---
              TextField(
                controller: pwController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: "Password",
                  border: OutlineInputBorder(),
                ),
              ),

              if (!isLogin) ...[
                const SizedBox(height: 15),
                TextField(
                  controller: nicknameController,
                  decoration: const InputDecoration(
                    labelText: "Nickname",
                    border: OutlineInputBorder(),
                  ),
                ),
              ],

              const SizedBox(height: 20),

              // 오류 메시지
              if (errorMessage != null)
                Text(
                  errorMessage!,
                  style: const TextStyle(color: Colors.red),
                ),

              const SizedBox(height: 20),

              // ---- Login Button ----
              ElevatedButton(
                onPressed: loading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: loading
                    ? const CircularProgressIndicator()
                    : Text(isLogin ? "로그인" : "회원가입"),
              ),

              TextButton(
                onPressed: () {
                  setState(() {
                    isLogin = !isLogin;
                    errorMessage = null;
                  });
                },
                child: Text(isLogin ? "회원가입으로 전환" : "로그인으로 전환"),
              ),

              const SizedBox(height: 10),
              const Text("또는", style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 10),

              // 소셜 로그인 버튼들
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: loading
                          ? null
                          : () => Api.oauthLogin(
                                "google",
                                redirect: "http://app.local/#/home",
                              ),
                      child: const Text("Google로 계속"),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: loading
                          ? null
                          : () => Api.oauthLogin(
                                "line",
                                redirect: "http://app.local/#/home",
                              ),
                      child: const Text("LINE으로 계속"),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
