import 'package:auto_doodle/screens/camera.dart';
import 'package:auto_doodle/screens/sensors.dart';
import 'package:flutter/material.dart';

class CameraSensors extends StatelessWidget {
  static String get route => '/camera';

  @override
  Widget build(BuildContext context) {
    final Size screenSize = MediaQuery.of(context).size;

    return Container(
      color: Colors.white,
      child: Stack(
        alignment: Alignment.center,
        children: [
          OverflowBox(
            maxHeight: screenSize.height,
            maxWidth: screenSize.width,
            child: Camera(),
          ),
          Positioned(
            child: BackSensor(),
            right: 0,
          )
        ],
      ),
    );
  }
}
