package foilingcatgdp.sailingstats;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.support.annotation.NonNull;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.res.ResourcesCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.SearchView;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import  android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedWriter;
import java.io.Console;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.RandomAccessFile;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;


public class DetailViewActivity extends AppCompatActivity {

    private BroadcastReceiver broadcastReceiver;
    TextView latValTxt;
    TextView longValTxt;
    TextView distValTxt;
    TextView speedValTxt;
    TextView statusTxt;
    TextView topRightTxt;
    LogDBHandler dbHandler;
    String startDateTime;
    double milliTimeOld;
    double milliTimeNew;
    int n;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detial_view);

        latValTxt = (TextView) findViewById(R.id.latValTxt);
        longValTxt = (TextView) findViewById(R.id.longValTxt);
        distValTxt = (TextView) findViewById(R.id.distValTxt);
        speedValTxt = (TextView) findViewById(R.id.speedValTxt);
        statusTxt = (TextView) findViewById(R.id.statusTxt);
        topRightTxt = (TextView) findViewById(R.id.topRightTxt);
        dbHandler = new LogDBHandler(this);

        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        //Check if permissions are needed and if ok enable the start/stop button.
        if(!runtime_permissions())
            enableButtons();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if(broadcastReceiver == null){
            broadcastReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {

                    //Get lat & long values from intent
                    double newLongVal = (double) intent.getExtras().get("long");
                    double newLatVal = (double) intent.getExtras().get("lat");
                    double ds = Double.NaN;
                    double dt = Double.NaN;
                    double speed = Double.NaN;
                    double heading = Double.NaN;
                    milliTimeNew = System.currentTimeMillis();

                    if(latValTxt.getText().toString() != "") { //Don't do first time round
                        //Get old values
                        double oldLongVal = Double.parseDouble(longValTxt.getText().toString());
                        double oldLatVal = Double.parseDouble(latValTxt.getText().toString());

                        //Calculate time step
                        dt = Math.abs(milliTimeNew - milliTimeOld)/1000;

                        //Calculate distance change
                        ds = distMovedCalc(oldLatVal, oldLongVal, newLatVal, newLongVal);
                        speed = (ds / dt) / 0.5144;

                        //Update Screen Text
                        distValTxt.setText(String.format("%.3f", ds));
                        speedValTxt.setText(String.format("%.3f", speed));
                    }

                    //Update Screen Text
                    longValTxt.setText(String.format("%.5f", newLongVal));
                    latValTxt.setText(String.format("%.5f", newLatVal));

                    //Update Read Time

                    milliTimeOld = milliTimeNew;

                    //Create data log entry
                    Date curDate = new Date();
                    SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy", Locale.UK);
                    SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm:ss.SSS", Locale.UK);
                    String dateString = dateFormat.format(curDate);
                    String timeString = timeFormat.format(curDate);

                    if (n > 9) {

                        FileWriter output = null;

                        try {
                            File outputFile = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "SailingStats" + File.separator + startDateTime + " Data.csv");
                            output = new FileWriter(outputFile, true);
                            output.write("\r\n" + dateString + "," + timeString + "," + newLatVal + "," + newLongVal + "," + ds + "," + dt + "," + speed + "," + heading);



                            System.out.println("Logged to:" + outputFile.getPath());
                            System.out.println("CSV Data File Size:" + outputFile.length());
                        } catch (FileNotFoundException e) {
                            e.printStackTrace();
                        } catch (IOException e) {
                            e.printStackTrace();
                        } finally {
                            try {
                                if (output != null) {
                                    output.close();
                                }
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        }
                        statusTxt.setGravity(Gravity.LEFT);
                        statusTxt.setText("Recording data...");
                        topRightTxt.setText((n - 9) + " Data Points");
                    }

                    n++;

                }
            };
        }
        registerReceiver(broadcastReceiver, new IntentFilter("location_update"));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        //Stop the GPS logging when closed
        if(broadcastReceiver != null){
            unregisterReceiver(broadcastReceiver);
        }
    }

    //Check if permissions are needed
    private boolean runtime_permissions() {
        if(Build.VERSION.SDK_INT >= 23 &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED&&
                ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED&&
                ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED){

            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.READ_EXTERNAL_STORAGE}, 100);

            return true;

        }
        return false;
    }

    //Enable buttons on permissions granted
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if(requestCode == 100){
            if(grantResults[0] == PackageManager.PERMISSION_GRANTED && grantResults[1] == PackageManager.PERMISSION_GRANTED && grantResults[2] == PackageManager.PERMISSION_GRANTED && grantResults[3] == PackageManager.PERMISSION_GRANTED){
                enableButtons();
            } else {
                runtime_permissions();
            }
        }
    }

    //Enable Start/Stop buttons
    private void enableButtons() {
        final Button startStreamBtn = (Button) findViewById(R.id.startStreamBtn);
        final Button stopStreamBtn = (Button) findViewById(R.id.stopStreamBtn);

        startStreamBtn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                Intent i = new Intent(getApplicationContext(), GPS_Service.class);
                startService(i);
                setBtnDown(true, startStreamBtn);
                setBtnDown(false, stopStreamBtn);
                Date curDate = new Date();
                SimpleDateFormat dateFormat = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss", Locale.UK);
                startDateTime = dateFormat.format(curDate);
                File output = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "SailingStats" + File.separator + startDateTime + " Data.csv");
                File output2 = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "SailingStats" + File.separator + startDateTime + " Data.gpx");
                try {
                    output.createNewFile();

                    Intent intent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
                    intent.setData(Uri.fromFile(output));
                    sendBroadcast(intent);

                    FileWriter outputFW = new FileWriter(output, true);
                    outputFW.write("Date,Time,Latitude,Longitude,Distance Change(m),Time Change (s),Speed (knots),Heading (deg)");


                } catch (IOException e) {
                    e.printStackTrace();
                }

                statusTxt.setText("Waiting for GPS...");
                n = 0;
            }
        });

        stopStreamBtn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                Intent i = new Intent(getApplicationContext(), GPS_Service.class);
                stopService(i);
                setBtnDown(false, startStreamBtn);
                setBtnDown(true, stopStreamBtn);
                longValTxt.setText("");
                latValTxt.setText("");
                distValTxt.setText("");
                speedValTxt.setText("");
                statusTxt.setText("");
            }
        });
    }

    //Calculate distance travelled
    private double distMovedCalc(double lat1, double lon1, double lat2, double lon2){
        double R = 6378.137; // Radius of earth in KM
        double dLat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180;
        double dLon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180;
        double a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                        Math.sin(dLon/2) * Math.sin(dLon/2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        double d = R * c;
        return d * 1000;
    }

    private void setBtnDown(boolean clicked, Button button){
        if(clicked){
            button.setBackgroundColor(ResourcesCompat.getColor(getResources(), R.color.colorPrimaryDark, null));
            button.setTextColor(ResourcesCompat.getColor(getResources(), R.color.colorAccent, null));
            button.setClickable(false);
        } else {
            button.setBackgroundColor(ResourcesCompat.getColor(getResources(), R.color.colorAccent, null));
            button.setTextColor(ResourcesCompat.getColor(getResources(), R.color.colorPrimaryDark, null));
            button.setClickable(true);
        }
    }


}
