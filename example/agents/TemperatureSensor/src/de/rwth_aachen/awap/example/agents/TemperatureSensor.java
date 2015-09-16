package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;
import de.rwth_aachen.awap.enums.TemperatureSensorType;

public class TemperatureSensor extends Agent {

	public void setup(){
		// initialize services
		new TemperatureService();
	}

	private class TemperatureService extends de.rwth_aachen.awap.service.local.TemperatureService {
		public TemperatureService() {
			super(TemperatureSensor.this, Building.Build1, SupplyCircuit.SC1, Room.R1, TemperatureSensorType.Troom);
		}

		public void onReceive(RequestTemperature msg) {
			// TODO: read temperature from hardware
			this.send(new Temperature(msg.remoteAgent, 1337));
		}
	}
}
