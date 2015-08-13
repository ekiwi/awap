package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.LocalAgent;
import de.rwth_aachen.awap.RemoteService;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.node.AbstractNode;
import de.rwth_aachen.awap.service.TemperatureServiceClient;

public class SimpleTemperatureSubscriber extends LocalAgent {

	public SimpleTemperatureSubscriber(byte id, AbstractNode node) {
		super(id, node);
	}


	public void setup() {
		new TemperatureClient(this);
	}

	private class TemperatureClient extends TemperatureServiceClient {

		public TemperatureClient(LocalAgent parent) {
			super(parent);
			// listen for any temperature service
			this.registerListener(new BuildingProperty(Building.Build1));
		}

		public void onReceive(Temperature msg) {
			System.out.println("Received Temperature: " + msg.value);
			System.out.println("From: " + msg.sender.id);
		}

		public void serviceFound(byte listenerId, RemoteService remoteService) {
			System.out.println("Found service: " + remoteService.remoteAgent.id);
			System.out.println("Trying to subscribe...");
			this.send(new Subscribe(remoteService));
		}

		public void serviceRemoved(byte listenerId,RemoteService remoteService) {
			System.out.println("Lost service: " + remoteService.remoteAgent.id);
		}

	}
}
