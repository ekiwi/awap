/**
 * SimpleTemperatureConsumer.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.messages.TemperatureService.RequestTemperature;
import de.rwth_aachen.awap.messages.TemperatureService.Temperature;
import de.rwth_aachen.awap.service.remote.ITemperatureServiceClient;
import de.rwth_aachen.awap.service.remote.TemperatureService;

public class SimpleTemperatureConsumer extends Agent implements ITemperatureServiceClient {
	private TemperatureService.Type temperaturSensorType;

	public void setup() {
		this.requestWakeUp(500);
		// temperature services in Building1 in Room1 or Room2
		this.temperaturSensorType = new TemperatureService.Type(
				this).building(Building.Build1).room(Room.R1);
	}

	public void onReceive(Temperature msg) {
		System.out.println("Received Temperature: " + msg.value);
		System.out.println("From: " + msg.remoteAgent.id);
	}

	public void onWakeUp(Object obj) {
		System.out.println("Agent: Woke up");
		this.temperaturSensorType.send(new RequestTemperature());
		this.requestWakeUp(1000);
	}

}
