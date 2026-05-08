#include <Adafruit_NeoPixel.h>
#include <ld2410.h>

#define LED_PIN 15
#define NUMPIXELS 30

Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
ld2410 radar;

void setup() {
  Serial.begin(115200);
  pixels.begin();
  pixels.setBrightness(20); 
  pixels.clear(); pixels.show();
  
  Serial2.begin(256000, SERIAL_8N1, 16, 17);
  radar.begin(Serial2);
  
  Serial.println("=== РЕЖИМ 'ВСЕЯДНЫЙ СНАЙПЕР' (ДВИЖЕНИЕ + СТАТИКА) ГОТОВ ===");
}

void loop() {
  radar.read();
  
  if (radar.isConnected()) {
    
    // 1. АКТИВАЦИЯ (Твой взмах рукой в Зоне 0)
    if (radar.movingTargetEnergy() > 40) {
      
      pixels.clear();
      for(int i=0; i<5; i++) pixels.setPixelColor(i, pixels.Color(0, 0, 255));
      pixels.show();
      
      Serial.println("\n[ТРИГГЕР] Махнул. Убегай!");
      
      // 2. ДАЕМ 3 СЕКУНДЫ НА ПОБЕГ 
      uint32_t t = millis();
      while(millis() - t < 3000) { radar.read(); }
      
      Serial.println("[ЗАМЕР] Ищу любую цель дальше 75 см...");
      
      pixels.clear();
      for(int i=0; i<5; i++) pixels.setPixelColor(i, pixels.Color(255, 255, 0));
      pixels.show();
      
      int count = 0;
      
      // 3. СКАНИРУЕМ КОМНАТУ (30 попыток)
      for (int i = 0; i < 30; i++) {
        radar.read(); 
        
        int target_dist = 0;
        int target_energy = 0;
        
        // ПРОВЕРЯЕМ СНАЧАЛА ДВИЖЕНИЕ (Вибрацию телефона)
        if (radar.movingTargetDetected() && radar.movingTargetDistance() >= 75) {
          target_dist = radar.movingTargetDistance();
          target_energy = radar.movingTargetEnergy();
        } 
        // ЕСЛИ ДВИЖЕНИЯ НЕТ, ПРОВЕРЯЕМ СТАТИКУ (Если фольга замерла)
        else if (radar.stationaryTargetDetected() && radar.stationaryTargetDistance() >= 75) {
          target_dist = radar.stationaryTargetDistance();
          target_energy = radar.stationaryTargetEnergy();
        }
        
        // 4. ЕСЛИ НАШЛИ ХОТЬ ЧТО-ТО ДАЛЬШЕ 75 см -> ПЕЧАТАЕМ
        if (target_dist >= 75) {
          Serial.print("ЗАМЕР | Дистанция: "); 
          Serial.print(target_dist); 
          Serial.print(" см | Энергия: "); 
          Serial.println(target_energy);
          
          count++;
          if (count >= 4) break; // Собрали 4 строчки - выходим
        }
        delay(100); 
      }
      
      if(count == 0) {
        Serial.println("Цель не найдена...");
      }
      
      pixels.clear(); pixels.show();
      
      // Глухая пауза 3 сек перед новым тестом
      t = millis();
      while(millis() - t < 3000) { radar.read(); }
    }
  }
}