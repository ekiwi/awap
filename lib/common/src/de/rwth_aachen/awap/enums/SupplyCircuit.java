package de.rwth_aachen.awap.enums;


public final class SupplyCircuit extends Enum {
	private SupplyCircuit(int value) { super(value); }
	public static final SupplyCircuit SC1 = new SupplyCircuit(0);
	public static final int NumberOfValues = 1;
}
