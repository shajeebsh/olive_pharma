import 'package:flutter/material.dart';

/// OlivePharma "Trusted Innovator" design tokens, mirrored from the web theme.
class AppTheme {
  const AppTheme._();

  static const Color primary = Color(0xFF008080); // Deep Teal
  static const Color navigation = Color(0xFF003566); // Dark Indigo
  static const Color background = Color(0xFFF8F9FA); // Cloud Dancer
  static const Color cardBorder = Color(0xFFE9ECEF); // Subtle Gray
  static const Color success = Color(0xFF10B981); // Emerald
  static const Color danger = Color(0xFFC2412C); // Terracotta
  static const Color warning = Color(0xFFF59E0B); // Amber

  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: primary,
      primary: primary,
      secondary: navigation,
      error: danger,
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: background,
      appBarTheme: const AppBarTheme(
        backgroundColor: navigation,
        foregroundColor: Colors.white,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: cardBorder),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: Colors.white,
        indicatorColor: primary.withOpacity(0.12),
        labelTextStyle: WidgetStateProperty.all(
          const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}
