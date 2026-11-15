import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/app_theme.dart';
import 'core/widgets/state_views.dart';
import 'features/auth/login_screen.dart';
import 'features/home/home_shell.dart';
import 'providers/auth_controller.dart';

class OliveApp extends ConsumerWidget {
  const OliveApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);

    return MaterialApp(
      title: 'OlivePharma Rep',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: switch (auth.status) {
        AuthStatus.unknown =>
          const Scaffold(body: LoadingView()),
        AuthStatus.authenticated => const HomeShell(),
        AuthStatus.unauthenticated => const LoginScreen(),
      },
    );
  }
}
