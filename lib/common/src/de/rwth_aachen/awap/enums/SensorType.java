package de.rwth_aachen.awap.enums;

public final class SensorType extends Enum {
	private SensorType(int value) { super(value); }
	public static final SensorType NotSet = new SensorType(0);
	public static final SensorType Tflow = new SensorType(1);
	public static final SensorType Treturn = new SensorType(2);
	public static final SensorType Toutside = new SensorType(3);
	public static final SensorType Troom = new SensorType(4);
	public static final int NumberOfValues = 5;
}
