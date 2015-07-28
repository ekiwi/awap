package de.rwth_aachen.awap.agents.temp_sensor;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.IDomainFacilitator;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;

public class TemperatureSensor extends Agent {
	private Building building;
	private SupplyCircuit supplyCircuit;
	private Room room;

	public TemperatureSensor(byte id, IDomainFacilitator df) {
		super(id,df);
	}


	public void setup(){

	}
}
