/**
 * SimpleTemperatureConsumer.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.example.agents;

import java.util.ArrayList;
import java.util.Iterator;

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
		this.requestWakeUp(500, new Integer(0));
		// temperature services in Building1 in Room1 or Room2
		this.temperaturSensorType = new TemperatureService.Type(
				this).building(Building.Build1).room(Room.R1);
	}

	class Result {
		public Result(Temperature msg) {
			this.senderId = msg.getRemoteAgent().id;
			this.value = msg.value;
			this.ttl = 3;
		}
		int senderId;
		int value;
		int ttl;
	}

	private ArrayList<Result> results = new ArrayList<Result>();

	public void onReceive(Temperature msg) {
		Result newRes = new Result(msg);
		// remove results from same sender
		Iterator it = results.iterator();
		while(it.hasNext()) {
			Result res = (Result)it.next();
			if(res.senderId == newRes.senderId) {
				it.remove();
			}
		}
		results.add(newRes);

		// System.out.println("Received Temperature: " + msg.value);
		// System.out.println("From: " + msg.getRemoteAgent().id);

	}

	private void displayResults() {
		// remove results and calculate maximum
		int max = 0;
		Iterator it = results.iterator();
		while(it.hasNext()) {
			Result res = (Result)it.next();
			res.ttl--;
			if(res.ttl <= 0) {
				it.remove();
			} else {
				if(res.value > max) {
					max = res.value;
				}
			}
		}

		// check if we are the maximum
		int localValue = this.node.getSensorValue();
		if(localValue >= max) {
			this.node.setActorValue(1);
			System.out.println("We have the largest value of: " + localValue);
		} else {
			this.node.setActorValue(0);
			System.out.println("The largest value is: " + max);
		}
	}

	public void onWakeUp(Object obj) {
		int ii = (Integer)obj;
		System.out.println("Agent: Woke up: " + ii);
		displayResults();
		this.temperaturSensorType.send(new RequestTemperature());
		this.requestWakeUp(1000, new Integer(ii+1));
	}

}
