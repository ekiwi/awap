package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.LocalAgent;
import de.rwth_aachen.awap.node.IDomainFacilitator;
import de.rwth_aachen.awap.service.TemperatureServiceClient;

public class SimpleTemperatureSubscriber extends LocalAgent {

	public SimpleTemperatureSubscriber(byte id, IDomainFacilitator df) {
		super(id, df);
	}


	public void setup() {
		new TemperatureClient(this);
	}

	private class TemperatureClient extends TemperatureServiceClient {

		public TemperatureClient(LocalAgent parent) {
			super(parent);
		}

		public void onFailedToSend(Subscribe msg) {
			if(msg.retransmissions < 2) {
				this.send(msg);
			}
		}

		public void onFailedToSend(Unsubscribe msg) {
			if(msg.retransmissions < 2) {
				this.send(msg);
			}
		}

		public void onReceive(Temperature msg) {
			System.out.println("Received Temperature: " + msg.value);
			System.out.println("From: " + msg.sender.id);
		}

	}
}
