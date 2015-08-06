package de.rwth_aachen.awap.example.agents;

import java.util.ArrayList;

import de.rwth_aachen.awap.LocalAgent;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;
import de.rwth_aachen.awap.node.IDomainFacilitator;
import de.rwth_aachen.awap.service.AbstractTemperatureService;

public class TemperatureSensor extends LocalAgent {
	public TemperatureSensor(byte id, IDomainFacilitator df) {
		super(id, df);
	}

	public void setup(){
		// initialize services
		this.registerService(new TemperatureService());
	}

	private class TemperatureService extends AbstractTemperatureService {
		public TemperatureService() {
			super(TemperatureSensor.this, Building.Build1, SupplyCircuit.SC1, Room.R1);
		}

		private ArrayList<RemoteAgent> subscribers;

		public void onReceive(Subscribe msg) {
			if(!this.subscribers.contains(msg.sender)) {
				this.subscribers.add(msg.sender);
				// send temperature to new subscriber
				this.send(new Temperature(msg.sender, (short)(1337)));
			}
		}

		public void onReceive(Unsubscribe msg) {
			if(this.subscribers.contains(msg.sender)){
				this.subscribers.remove(msg.sender);
			}
		}

		public void onFailedToSend(Temperature msg) {
			if(msg.retransmissions < 2) {
				this.send(msg);
			}
		}

	}
}
