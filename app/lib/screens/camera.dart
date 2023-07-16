import 'package:auto_doodle/API/toaster.dart';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

enum CameraState { loading, not_found, found, error }

class Camera extends StatefulWidget {
  const Camera({super.key});

  @override
  State<Camera> createState() => _CameraState();
}

class _CameraState extends State<Camera> {
  late CameraController controller;
  CameraState state = CameraState.loading;

  @override
  void initState() {
    availableCameras().then((List<CameraDescription> cameras_found) {
      if (cameras_found.isNotEmpty) {
        controller = CameraController(cameras_found.first, ResolutionPreset.max,
            enableAudio: false);
        controller.initialize().then((_) {
          controller.lockCaptureOrientation(DeviceOrientation.landscapeRight);
          setState(() {
            state = CameraState.found;
          });
        }).catchError((Object e) {
          Toaster.debug('$e');
          setState(() {
            state = CameraState.error;
          });
        });
      } else {
        setState(() {
          state = CameraState.not_found;
        });
      }
    });
    super.initState();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return switch (state) {
      CameraState.loading => const SpinKitSpinningLines(color: Colors.blue),
      CameraState.not_found => const Text(
          "No camera found",
          style: TextStyle(color: Colors.yellow),
        ),
      CameraState.error => const Text(
          "Error",
          style: TextStyle(color: Colors.red),
        ),
      CameraState.found => CameraPreview(controller),
    };
  }
}
