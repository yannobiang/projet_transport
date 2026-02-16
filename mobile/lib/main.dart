import 'package:flutter/material.dart';
import 'package:mobile/core/configs/theme/app_theme.dart';
import 'package:mobile/presentation/splash/pages/splash.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Urban Transport',
      theme: AppTheme.lightTheme,
      home: const  SplashPage()
    );
  }
}

