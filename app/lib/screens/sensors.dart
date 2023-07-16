import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class Sensor extends StatelessWidget {
  final double? value;
  final String name;
  final Icon icon;
  final String unit;
  const Sensor(this.name, this.icon, this.value, this.unit, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 130.0,
      height: 130.0,
      child: Card(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  name,
                  style: TextStyle(color: Colors.black, fontSize: 20),
                ),
                icon,
              ],
            ),
            (value == null)
                ? SpinKitSpinningLines(
                    color: Colors.blue,
                    size: 50.0,
                  )
                : Text(
                    "${value!.toStringAsFixed(2)} $unit",
                    style: TextStyle(color: Colors.black, fontSize: 20),
                  ),
          ],
        ),
      ),
    );
  }
}
