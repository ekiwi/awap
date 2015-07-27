package de.rwth_aachen.awap.enums;


public final class Building extends Enum {
	private Building(int value) { super(value); }
	public static final Building Build1 = new Building(0);
	public static final int NumberOfValues = 1;
}
