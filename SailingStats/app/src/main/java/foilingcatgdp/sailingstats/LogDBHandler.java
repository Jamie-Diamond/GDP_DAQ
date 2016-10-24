package foilingcatgdp.sailingstats;

import android.content.Context;
import android.content.ContentValues;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class LogDBHandler extends SQLiteOpenHelper {

    private static final int DATABASE_VERSION = 1;
    private static final String DATABASE_NAME = "DataLog.db";
    public static final String TABLE_NAME = "DataTable";
    public static final String COLUMN_ID = "id";
    public static final String COLUMN_DATE = "Date";
    public static final String COLUMN_TIME = "Time";
    public static final String COLUMN_LAT = "Latitude";
    public static final String COLUMN_LONG = "Longitude";
    public static final String COLUMN_DISTANCE = "Distance_m";
    public static final String COLUMN_SPEED = "Speed_knots";
    public static final String COLUMN_HEADING = "Heading_deg";

    //Initialise database
    public LogDBHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    //Create the table when we create this class
    @Override
    public void onCreate(SQLiteDatabase db) {
        String query = "CREATE TABLE " + TABLE_NAME + "(" +
                COLUMN_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
                COLUMN_DATE + " TEXT, " +
                COLUMN_TIME + " TEXT, " +
                COLUMN_LAT + " FLOAT, " +
                COLUMN_LONG + " FLOAT, " +
                COLUMN_DISTANCE + " FLOAT, " +
                COLUMN_SPEED + " FLOAT, " +
                COLUMN_HEADING + " FLOAT" +
                ");";

        db.execSQL(query);
    }

    //If we upgrade the table version, delete the old one to avoid confusion
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
        onCreate(db);
    }

    //Add new row to the database.
    public  void addElementToDB (DataLogElement data){
        ContentValues values = new ContentValues();
        values.put(COLUMN_DATE, data.get_date());
        values.put(COLUMN_TIME, data.get_time());
        values.put(COLUMN_LAT, data.get_lat());
        values.put(COLUMN_LONG, data.get_long());
        values.put(COLUMN_DISTANCE, data.get_distance());
        values.put(COLUMN_SPEED, data.get_speed());
        values.put(COLUMN_HEADING, data.get_heading());

        SQLiteDatabase db = getWritableDatabase();
        db.insert(TABLE_NAME, null, values);
        db.close();
    }
}
