package de.rwth_aachen.awap.enums;

public final class ServiceType extends Enum {
	private ServiceType(int value) { super(value); }
	public static final ServiceType ActorValveAgent = new ServiceType(0);
	public static final ServiceType ComfortAgent = new ServiceType(1);
	public static final ServiceType RoomAgent = new ServiceType(2);
	public static final ServiceType SensorTempAgent = new ServiceType(3);
	public static final ServiceType EnergySupplyAgent = new ServiceType(4);
	public static final int NumberOfValues = 5;
}
