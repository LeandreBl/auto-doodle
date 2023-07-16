import 'package:auto_doodle/API/autoDoodle.dart';
import 'package:auto_doodle/screens/camera.dart';
import 'package:auto_doodle/screens/sensors.dart';
import 'package:floating/floating.dart';
import 'package:flutter/material.dart';

class CameraSensors extends StatefulWidget {
  static String get route => '/camera';

  @override
  State<CameraSensors> createState() => _CameraSensorsState();
}

class _CameraSensorsState extends State<CameraSensors> {
  AutoDoodleAPI api = AutoDoodleAPI();
  double? frontDistance = null;
  double? backDistance = null;
  double? boardTemp = null;
  final Floating floating = Floating();

  @override
  void dispose() {
    floating.dispose();
    api.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    api.connect(onConnect: () {
      api.subscribe("back_distance_sensor");
      api.subscribe("board_temperature");
      //api.subscribe("front_distance_sensor");
    }, onDisconnect: () {
      setState(() {
        frontDistance = null;
        backDistance = null;
        boardTemp = null;
      });
    });
    api.on("notify_values", (dynamic data) {
      final double value = data["values"]["value"] as double;
      setState(() {
        switch (data["service"]) {
          case "back_distance_sensor":
            backDistance = value * 100;
          case "front_distance_sensor":
            frontDistance = value * 100;
          case "board_temperature":
            boardTemp = value;
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final Size screenSize = MediaQuery.of(context).size;

    return PiPSwitcher(
      childWhenEnabled: Camera(),
      childWhenDisabled: Container(
        color: Colors.white,
        child: Stack(
          alignment: Alignment.center,
          children: [
            OverflowBox(
              maxHeight: screenSize.height,
              maxWidth: screenSize.width,
              child: Card(
                child: Camera(),
              ),
            ),
            Positioned(
              bottom: 0,
              right: 0,
              child: Card(
                child: IconButton(
                  icon: Icon(Icons.exit_to_app),
                  onPressed: () {
                    floating.enable();
                  },
                ),
              ),
            ),
            Positioned(
                left: 0,
                child: Column(
                  children: [
                    Container(
                      margin: EdgeInsets.only(left: 15, top: 15, right: 15),
                      child: Sensor(
                          "Board",
                          Icon(
                            Icons.thermostat,
                            color: Colors.red,
                          ),
                          boardTemp,
                          "°C"),
                    ),
                  ],
                )),
            Positioned(
              right: 0,
              child: Column(
                children: [
                  Container(
                    margin: EdgeInsets.only(left: 15, top: 15, right: 15),
                    child: Sensor("Front", Icon(Icons.keyboard_double_arrow_up),
                        frontDistance, "cm"),
                  ),
                  Container(
                    margin: EdgeInsets.only(left: 15, top: 15, right: 15),
                    child: Sensor(
                        "Back",
                        Icon(Icons.keyboard_double_arrow_down),
                        backDistance,
                        "cm"),
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
