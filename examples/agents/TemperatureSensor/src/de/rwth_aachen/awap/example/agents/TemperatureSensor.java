package de.rwth_aachen.awap.example.agents;

import java.util.ArrayList;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;
import de.rwth_aachen.awap.node.AbstractNode;

public class TemperatureSensor extends Agent {
	public TemperatureSensor(byte id, AbstractNode node) {
		super(id, node);
	}

	public void setup(){
		// initialize services
		new TemperatureService();
	}

	private class TemperatureService extends de.rwth_aachen.awap.service.local.TemperatureService {
		public TemperatureService() {
			super(TemperatureSensor.this, Building.Build1, SupplyCircuit.SC1, Room.R1);
		}

		private ArrayList<RemoteAgent> subscribers;

		public void onReceive(Subscribe msg) {
			if(!this.subscribers.contains(msg.remoteAgent)) {
				this.subscribers.add(msg.remoteAgent);
				// send temperature to new subscriber
				this.send(new Temperature(msg.remoteAgent, (short)(1337)));
			}
		}

		public void onReceive(Unsubscribe msg) {
			if(this.subscribers.contains(msg.remoteAgent)){
				this.subscribers.remove(msg.remoteAgent);
			}
		}
	}
}
