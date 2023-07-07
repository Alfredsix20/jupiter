/* serial-control - Código de ejemplo para utilizar el puerto serial en comunicación birireccional
 * con mensajes de texto en formato de valores separados por comas (CSV).
 * El nodo de Arduino funciona en modo 'esclavo': únicamente responde a una comunicación
 * iniciada por el otro nodo 'maestro'.
 * Funciona en Arduino Uno, Nano, Mega, ESP32 y similares.
 * Para un ejemplo de comunicación serial con Python, consultar:
 * https://github.com/cmoralesd/serial-comm
 */


// parámetros de la tarjeta
#define led_0  5  // led verde
#define led_1  6  // led rojo
#define in_x  A0  // VRx 
#define in_y  A1  // VRy

// parámetros de configuración para comunicación
const int BAUD_RATE = 9600; // velocidad de comunicación
const char SPLIT_CHAR = ','; // caracter de separacion
const int DATA_LENGHT = 2; // número de valores contenidos en el mensaje recibido
int data[DATA_LENGHT];  // se esperan valores de tipo (int) en el mensaje recibido

// variables globales
String buffer = ""; // almacena los caracteres recibidos desde el puerto serial, hasta conformar el mensaje
String message_from_serial = ""; // almacena el mensaje recibido desde el puerto serial
String message_to_serial = "";   // almacena el mensaje a ser enviado hacia el puerto serial
bool new_message_from_serial = false;    // true si se ha recibido un nuevo mensaje completo


void setup() {
  // inicializa puerto serial a la velocidad definida en la configuración
  Serial.begin(BAUD_RATE);
  // espera a que el puerto se inicialice
  delay(100);  
  // limpia cualquier dato que esté alojado en el buffer
  while (Serial.available()) { char inChar = Serial.read();}
  Serial.println("Arduino OK");
 
  // configura pines I/O
  pinMode(led_0, OUTPUT);
  pinMode(led_1, OUTPUT);

}

void loop() {
  // inspecciona cíclicamente el puerto serie
  serialEvent();

  if (new_message_from_serial){
    /*
     * Esta parte del código se ejecuta cada vez que se recibe un nuevo mensaje completo.
     * El último mensaje recibido se encuentra almacenado en 'message_from_serial'
    */ 
    
    // 1. Procesar el mensaje recibido
    split_values(message_from_serial);
    bool out_0 = (bool) data[0];
    int out_1 = (int) data[1];
    digitalWrite(led_0, out_0);
    analogWrite(led_1, out_1);

    // 2. Preparar el mensaje de respuesta
    int input_0 = analogRead(in_x);
    int input_1 = analogRead(in_y);
    message_to_serial = String(input_0) + ';' + String(input_1);

    // 3. Enviar la respuesta y restablecer la bandera
    Serial.println(message_to_serial);
    Serial.flush(); // espera hasta que el mensaje salga del buffer
    new_message_from_serial = false;


  }

  /*
     * Esta parte del código se ejecuta siempre.
     * IMPORTANTE: Evite agregar retardos (delay) dentro de loop()
    */

  

}

void serialEvent() {
  while (Serial.available()) {
    // recibe nuevo byte
    int inChar = Serial.read();
    // lo agrega al mensaje recibido
    buffer += (char) inChar;
    // si se recibe un final de linea, se levanta una bandera,
    // de forma que el ciclo frincipal pueda hacer algo con eso:
    if (inChar == '\n') {
      message_from_serial = buffer;
      new_message_from_serial = true;
      buffer = "";
      break;
    }
  }
}

void split_values(String msg){
    // recibe un mensaje de tipo String, que contiene valores de tipo (int), separados 
    // por un caracter de separación 'SPLIT_CHAR', definido en la configuración. 
    // Los valores separados se almacenan en el array 'data'
    for (int i = 0; i < sizeof(data) ; i++)
    {
      int index = msg.indexOf(SPLIT_CHAR);
      data[i] = msg.substring(0, index).toInt();
      msg = msg.substring(index + 1);
    }

}
