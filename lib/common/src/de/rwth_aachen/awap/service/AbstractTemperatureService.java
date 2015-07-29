package de.rwth_aachen.awap.service;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.Service;

public abstract class AbstractTemperatureService extends Service {
	protected byte building;
	protected byte supplyCircuit;
	protected byte room;
	public AbstractTemperatureService(Agent parent, byte building, byte supplyCircuit, byte room) {
		super(parent);
		// TODO: instead of setting protected values => register with df
		this.building = building;
		this.supplyCircuit = supplyCircuit;
		this.room = room;
	}
	public abstract void onReceiveSubscribe(RemoteAgent sender);
	public abstract void onReceiveUnsubscribe(RemoteAgent sender);
	public abstract void onFailedToSendTemperature(RemoteAgent receiver, int value);
	public void sendTemperature(RemoteAgent receiver, int value) {
		// TODO: generate message and dispatch
	}
}
