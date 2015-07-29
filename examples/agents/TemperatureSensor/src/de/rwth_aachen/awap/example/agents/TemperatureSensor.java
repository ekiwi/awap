package de.rwth_aachen.awap.example.agents;

import java.util.ArrayList;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.IDomainFacilitator;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.enums.SupplyCircuit;
import de.rwth_aachen.awap.service.AbstractTemperatureService;

public class TemperatureSensor extends Agent {
	private TemperatureService temperatureService;


	public TemperatureSensor(byte id, IDomainFacilitator df) {
		super(id, df);
	}


	public void setup(){
		this.temperatureService = new TemperatureService();
	}

	public void tearDown() {

	}

	private class TemperatureService extends AbstractTemperatureService {
		public TemperatureService() {
			super(TemperatureSensor.this, Building.Build1, SupplyCircuit.SC1, Room.R1);
		}

		private ArrayList<RemoteAgent> subscribers;

		public void onReceiveSubscribe(RemoteAgent sender) {
			if(!this.subscribers.contains(sender)) {
				this.subscribers.add(sender);
				// send temperature to new subscriber
				this.sendTemperature(sender, 1337);
			}
		}

		public void onReceiveUnsubscribe(RemoteAgent sender) {
			if(this.subscribers.contains(sender)){
				this.subscribers.remove(sender);
			}
		}

		public void onFailedToSendTemperature(RemoteAgent receiver, int value) {
			// FIXME: give up after x tries
			this.sendTemperature(receiver, value);
		}

	}
}
