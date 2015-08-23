package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.node.AbstractNode;
import de.rwth_aachen.awap.service.remote.ITemperatureServiceClient;
import de.rwth_aachen.awap.service.remote.TemperatureService;
import de.rwth_aachen.awap.service.remote.TemperatureService.Temperature;

public class SimpleTemperatureSubscriber extends Agent implements ITemperatureServiceClient {

	public void setup() {
		TemperatureService.registerListener(this, new TemperatureService.BuildingProperty(Building.Build1));
	}

	public void serviceFound(byte listenerId, TemperatureService service) {
		System.out.println("Found service: " + service.remoteAgent.id);
		System.out.println("Trying to subscribe...");
		service.send(new TemperatureService.Subscribe());
	}


	public void serviceRemoved(byte listenerId, TemperatureService service) {
		System.out.println("Lost service: " + service.remoteAgent.id);
	}


	public void onReceive(Temperature msg) {
		System.out.println("Received Temperature: " + msg.value);
		System.out.println("From: " + msg.remoteAgent.id);
	}
}
