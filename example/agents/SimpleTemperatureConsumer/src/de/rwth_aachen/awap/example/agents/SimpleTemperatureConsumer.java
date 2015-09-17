package de.rwth_aachen.awap.example.agents;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.enums.Building;
import de.rwth_aachen.awap.enums.Room;
import de.rwth_aachen.awap.service.remote.ITemperatureServiceClient;
import de.rwth_aachen.awap.service.remote.TemperatureService;
import de.rwth_aachen.awap.service.remote.TemperatureService.Temperature;

public class SimpleTemperatureConsumer extends Agent implements ITemperatureServiceClient {
	private TemperatureService.Type temperaturSensorType;

	public void setup() {
		this.requestWakeUp(500);
		// temperature services in Building1 in Room1 or Room2
		this.temperaturSensorType = new TemperatureService.Type(
				this).building(Building.Build1).room(Room.R1, Room.R2);
	}

	public void onReceive(Temperature msg) {
		System.out.println("Received Temperature: " + msg.value);
		System.out.println("From: " + msg.remoteAgent.id);
	}

	public void onWakeUp() {
		this.temperaturSensorType.send(new TemperatureService.RequestTemperature());
		this.requestWakeUp(500);
	}

}