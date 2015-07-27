package de.rwth_aachen.awap.enums;

public class ServiceName extends Enum {
	private ServiceName(int value) { super(value); }
	public static final ServiceName TemperatureAgent = new ServiceName(0);
	public static final int NumberOfValues = 1;
}
