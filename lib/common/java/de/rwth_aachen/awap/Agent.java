/**
 * Agent.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

import java.util.ArrayList;

public abstract class Agent {
	private int id;
	private ArrayList<LocalService> services = new ArrayList<LocalService>();
	private ArrayList<Object> callbackObjects = new ArrayList<Object>();
	public AbstractNode node;

	/**
	 * will be called immediately after the constructor
	 */
	public void init(int id, AbstractNode node) {
		this.id = id;
		this.node = node;
	}

	public int getId() {
		return id;
	}

	protected byte registerService(LocalService service) {
		for(LocalService serv : this.services) {
			if(serv.serviceId == service.serviceId) {
				// ERROR: can only have one service of a kind per agent
				return -1;
			}
		}
		if(this.node.registerService(service)) {
			// FIXME: this is not thread save
			this.services.add(service);
			return (byte)(this.services.size() - 1);
		} else {
			return -1;
		}
	}

	/**
	 * This method is called when the agent is installed on a node.
	 */
	public abstract void setup();

	protected final void requestWakeUp(int milliseconds) {
		// 0xff always means null
		this.node.requestWakeUp(milliseconds, (byte)0xff);
	}


	protected final void requestWakeUp(int milliseconds, Object obj) {
		// put obj into array list
		// check if there are empty spots
		for(short ii = 0; ii < callbackObjects.size(); ++ii) {
			if(callbackObjects.get(ii) == null) {
				callbackObjects.set(ii, obj);
				this.node.requestWakeUp(milliseconds, (byte)ii);
				return;
			}
		}
		// if not insert at the end
		callbackObjects.add(obj);
		this.node.requestWakeUp(milliseconds, (byte)(callbackObjects.size()-1));
	}

	public final void wakeUp(byte index) {
		if(index == (byte)0xff) {
			this.onWakeUp(null);
		} else {
			// retrieve object
			Object obj = callbackObjects.get(index);
			callbackObjects.set(index, null);
			// call agent
			this.onWakeUp(obj);
		}
	}

	/**
	 * This method is called when a timeout expires
	 */
	public void onWakeUp(Object obj) {
		// default: do nothing
	}

	/**
	 * This method is called when the platform is about to shut down.
	 */
	public void tearDown() {
		for(LocalService service : this.services) {
			this.node.deregisterService(service);
		}
	}

	public boolean handleLocalServiceMessage(Message msg) {
		for(LocalService service : this.services) {
			if(service.serviceId == msg.serviceTypeId) {
				return service.handleMessage(msg);
			}
		}
		return false;
	}
}
