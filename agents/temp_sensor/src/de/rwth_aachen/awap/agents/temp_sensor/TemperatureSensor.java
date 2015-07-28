package de.rwth_aachen.awap.agents.temp_sensor;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.IDomainFacilitator;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.ServiceType;
import de.rwth_aachen.awap.properties.PBuilding;
import de.rwth_aachen.awap.properties.Property;

public class TemperatureSensor extends Agent {
	private byte temperatureServiceId;


	public TemperatureSensor(byte id, IDomainFacilitator df) {
		super(id, df);
	}


	public void setup(){
		Property[] props = { new PBuilding(Building.Build1) };
		this. temperatureServiceId =
				this.df.registerService(ServiceType.SensorTempAgent, props);
	}

	public void tearDown() {
		this.df.deregisterService(this.temperatureServiceId);
	}
}
