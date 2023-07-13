import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:flutter/foundation.dart' as foundation;

class Toaster {
  static void debug(String message) {
    if (foundation.kDebugMode) {
      _addToast(
        '@DEBUG\n$message',
        backgroundColor: Colors.black,
        textColor: Colors.yellowAccent,
      );
    }
  }

  static void success(String message) {
    _addToast(
      message,
      textColor: Colors.green,
    );
  }

  static void info(String message) {
    _addToast(
      message,
      textColor: Colors.yellow,
    );
  }

  static void warning(String message) {
    _addToast(
      message,
      textColor: Colors.deepPurple,
    );
  }

  static void alert(String message) {
    _addToast(
      message,
      textColor: Colors.red,
    );
  }

  static void _addToast(
    String message, {
    Toast toastLength = Toast.LENGTH_SHORT,
    ToastGravity gravity = ToastGravity.BOTTOM,
    Color backgroundColor = Colors.white,
    Color textColor = Colors.black,
    double fontSize = 16.0,
  }) {
    Fluttertoast.showToast(
      msg: message,
      toastLength: toastLength,
      gravity: gravity,
      timeInSecForIosWeb: 1,
      backgroundColor: backgroundColor,
      textColor: textColor,
      fontSize: fontSize,
    );
  }

  static void dismiss() {
    Fluttertoast.cancel();
  }
}
