package foilingcatgdp.sailingstats;

public class DataLogElement {

    private int _id;
    private String _date;
    private String _time;
    private double _lat;
    private double _long;
    private double _distance;
    private double _speed;
    private double _heading;


    public void DataLogElement() {}

    public DataLogElement(String date, String time, double lat, double lon, double distance, double speed, double heading) {
        this._date = date;
        this._distance = distance;
        this._heading = heading;
        this._lat = lat;
        this._long = lon;
        this._speed = speed;
        this._time = time;
    }

    public double get_heading() {
        return _heading;
    }

    public void set_heading(double _heading) {
        this._heading = _heading;
    }

    public String get_date() {
        return _date;
    }

    public void set_date(String _date) {
        this._date = _date;
    }

    public double get_distance() {
        return _distance;
    }

    public void set_distance(double _distance) {
        this._distance = _distance;
    }

    public double get_lat() {
        return _lat;
    }

    public void set_lat(double _lat) {
        this._lat = _lat;
    }

    public double get_long() {
        return _long;
    }

    public void set_long(double _long) {
        this._long = _long;
    }

    public String get_time() {
        return _time;
    }

    public void set_time(String _time) {
        this._time = _time;
    }

    public double get_speed() {
        return _speed;
    }

    public void set_speed(double _speed) {
        this._speed = _speed;
    }
}
