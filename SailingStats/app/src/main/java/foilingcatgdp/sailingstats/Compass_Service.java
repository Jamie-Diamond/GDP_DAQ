package foilingcatgdp.sailingstats;

import android.app.Activity;
import android.app.Service;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.IBinder;
import android.support.annotation.Nullable;

import java.util.Arrays;

public class Compass_Service extends Service implements SensorEventListener {
    SensorManager sm;

    @Override
    public void onCreate() {
        super.onCreate();
        System.out.println("Compass Service started.");
        sm = (SensorManager) getSystemService(SENSOR_SERVICE);

        // Register this class as a listener for the accelerometer sensor
        sm.registerListener(this, sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
                SensorManager.SENSOR_DELAY_NORMAL);
        // ...and the orientation sensor
        sm.registerListener(this, sm.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD),
                SensorManager.SENSOR_DELAY_NORMAL);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        //System.out.println("Compass sensor update");
        float[] inR = new float[16];
        float[] I = new float[16];
        float[] gravity = new float[3];
        float[] geomag = new float[3];
        float[] orientVals = new float[3];

        double heading = Double.NaN;
        double pitch = Double.NaN;
        double roll = Double.NaN;

        // If the sensor data is unreliable return
        if (event.accuracy == sm.SENSOR_STATUS_UNRELIABLE){
            System.out.println("Unreliable sensor reading: " + event.sensor.getStringType());
            return;
        }

        // Gets the value of the sensor that has been changed
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                gravity = event.values.clone();
                System.out.println("Grav sensor update");
                break;
            case Sensor.TYPE_MAGNETIC_FIELD:
                geomag = event.values.clone();
                System.out.println("Geomag sensor update");
                break;
        }

        // If gravity and geomag have values then find rotation matrix
        if (gravity != null && geomag != null) {
            //System.out.println(Arrays.toString(gravity) + " , " + Arrays.toString(geomag));

            // checks that the rotation matrix is found
            boolean success = SensorManager.getRotationMatrix(inR, I, gravity, geomag);
            //System.out.println(success);

            if (success) {
                System.out.println("Rotation found. Getting orientation");
                SensorManager.getOrientation(inR, orientVals);
                heading = Math.toDegrees(orientVals[0]);
                pitch = Math.toDegrees(orientVals[1]);
                roll = Math.toDegrees(orientVals[2]);
            }
        }


        Intent i = new Intent("compass_update");
        i.putExtra("heading", heading);
        i.putExtra("compassPitch", pitch);
        i.putExtra("compassRoll", roll);
        sendBroadcast(i);
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        sm.unregisterListener(this);
        System.out.println("Compass Service stopped.");
    }
}

