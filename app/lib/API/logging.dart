import 'package:logger/logger.dart';

final Logger logger = Logger(
  level: Level.debug,
  printer: PrettyPrinter(
    methodCount: 3,
    printTime: true
  ),
);

class Logging {
  static void debug(String message) =>
      logger.d(message);

  static void info(String message) =>
      logger.i(message);

  static void warning(String message) =>
      logger.w(message);

  static void error(String message) =>
      logger.e(message);

  static void fatal(String message) =>
      logger.wtf(message);
}
