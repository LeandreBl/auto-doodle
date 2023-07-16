import 'package:socket_io_client/socket_io_client.dart' as IO;

const String DEFAULT_URL = 'localhost';
const int DEFAULT_PORT = 8000;

class AutoDoodleAPI {
  late IO.Socket ws;
  final String uri;

  AutoDoodleAPI({String this.uri = 'ws://$DEFAULT_URL:$DEFAULT_PORT'}) {}

  void connect({void Function()? onConnect, void Function()? onDisconnect, void Function()? onError}) {
    ws = IO.io(
        uri,
        IO.OptionBuilder()
            .setTransports(['websocket'])
            .build());
    ws.onConnect((_) {
      if (onConnect != null) {
        onConnect();
      }
    });
    ws.onDisconnect((_) {
      if (onDisconnect != null) {
        onDisconnect();
      }
    });
    ws.onError((_) {
      if (onError != null) {
        onError();
      }
    });
  }

  void dispose() {
    ws.disconnect();
    ws.dispose();
  }

  void __send(String event, dynamic packet) {
    ws.emit(event, packet);
  }

  void on(String event, void Function(dynamic data) callback) {
    ws.on(event, callback);
  }

  void subscribe(String service) {
    __send("subscribe", {"service_name": service});
  }

  void unsubscribe(String service) {
    __send("subscribe", {"service_name": service});
  }

  void getSubscriptions() {
    __send("get_subscriptions", null);
  }

  void setUsername(String username) {
    __send("set_username", {"username": username});
  }
}
