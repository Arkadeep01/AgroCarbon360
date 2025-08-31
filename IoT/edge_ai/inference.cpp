/* inference.cpp
   Minimal TensorFlow Lite Micro example for ESP32/Arduino.
   - You must build with the TFLite Micro library available in your Arduino/ESP32 environment.
   - Convert your .tflite model to a C array (model_data[]) and include it here or as a header.
   - Example: xxd -i model.tflite > model_data.cc
*/

#include <Arduino.h>
#include "TensorFlowLite.h"  // your environment must provide TFLM headers
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

// Include your C array converted model
// #include "crop_reco_model_data.h"  // contains 'unsigned char crop_reco_model[]' and length

// For example placeholder:
// extern const unsigned char crop_reco_model[];
// extern const int crop_reco_model_len;

#define TENSOR_ARENA_SIZE 30 * 1024  // adjust based on model size
static uint8_t tensor_arena[TENSOR_ARENA_SIZE];

// --------- Replace these with actual model array/length ---------
extern const unsigned char crop_reco_model[];  // provide via model_data header
extern const int crop_reco_model_len;
// ----------------------------------------------------------------

using namespace tflite;

void setup() {
  Serial.begin(115200);
  while (!Serial) ; // wait for Serial
  Serial.println("TFLM ESP32 inference starting...");

  // Map the model
  const tflite::Model* model = tflite::GetModel(crop_reco_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema version mismatch!");
    while (1);
  }

  // Ops resolver
  static tflite::AllOpsResolver resolver;

  // Interpreter
  static tflite::MicroInterpreter interpreter(
    model, resolver, tensor_arena, TENSOR_ARENA_SIZE, nullptr);

  TfLiteStatus allocate_status = interpreter.AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    Serial.println("AllocateTensors() failed");
    while (1);
  }

  Serial.println("Interpreter ready.");
}

float normalize_clip(float x, float vmin, float vmax) {
  if (x < vmin) x = vmin;
  if (x > vmax) x = vmax;
  float scaled = 2.0f * ((x - vmin) / (vmax - vmin + 1e-6f)) - 1.0f;
  return scaled;
}

void loop() {
  // Read sensors here (mocked values for demo)
  float soil_moisture = 35.0;
  float soil_ph = 6.4;
  float soil_temp_c = 28.0;
  float air_temp_c = 30.0;
  float rain_last_7d_mm = 45.0;
  float ec = 1.2;

  // Preprocess to match model input order and scale
  // IMPORTANT: input shape and order must match what model expects!
  // Example feature order:
  float input_vals[6];
  input_vals[0] = normalize_clip(soil_moisture, 0.0, 100.0);
  input_vals[1] = normalize_clip(soil_ph, 3.0, 9.0);
  input_vals[2] = normalize_clip(soil_temp_c, -5.0, 50.0);
  input_vals[3] = normalize_clip(air_temp_c, -10.0, 55.0);
  input_vals[4] = normalize_clip(rain_last_7d_mm, 0.0, 500.0);
  input_vals[5] = normalize_clip(ec, 0.0, 10.0);

  // Get interpreter and tensors (recreate to keep example simple)
  const tflite::Model* model = tflite::GetModel(crop_reco_model);
  static tflite::AllOpsResolver resolver;
  static tflite::MicroInterpreter interpreter(model, resolver, tensor_arena, TENSOR_ARENA_SIZE, nullptr);
  interpreter.AllocateTensors();

  TfLiteTensor* input = interpreter.input(0);
  // assert input type and size
  if (input->type != kTfLiteFloat32) {
    Serial.println("Model input type is not float32!");
    delay(5000);
    return;
  }

  // Assuming input->bytes == sizeof(float)*6 and dims match
  float* input_buffer = input->data.f;
  for (int i=0;i<6;i++) input_buffer[i] = input_vals[i];

  // Run
  TfLiteStatus invoke_status = interpreter.Invoke();
  if (invoke_status != kTfLiteOk) {
    Serial.println("Invoke failed!");
    delay(2000);
    return;
  }

  // Read output (example: classification with N labels)
  TfLiteTensor* output = interpreter.output(0);
  int out_len = output->bytes / sizeof(float);
  Serial.print("Output probabilities: ");
  for (int i=0;i<out_len;i++) {
    float v = output->data.f[i];
    Serial.print(v, 4);
    Serial.print(" ");
  }
  Serial.println();

  // Postprocessing could map highest prob to a crop
  // Sleep for a while before next inference
  delay(10 * 1000);
}
