import 'package:auto_doodle/API/autoDoodle.dart';
import 'package:auto_doodle/API/logging.dart';
import 'package:flutter/material.dart';

class BackSensor extends StatefulWidget {
  const BackSensor({super.key});

  @override
  State<BackSensor> createState() => _BackSensorState();
}

class _BackSensorState extends State<BackSensor> {
  double? distance = null;
  AutoDoodleAPI api = AutoDoodleAPI();

  @override
  void initState() {
    super.initState();
    api.connect(onConnect: () {
      Logging.debug("connected");
      api.subscribe("back_distance_service");
    });
    api.on("notify_values", (dynamic data) {
      if (data["service"] == "back_distance_sensor") {
        setState(() {
          distance = data["values"]["distance"] as double;
        });
        Logging.debug("$distance");
      }
    });
  }

  @override
  void dispose() {
    api.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    switch (distance) {
      case null:
        return Text("loading...");
      default:
        return Text("$distance m");
    }
  }
}
