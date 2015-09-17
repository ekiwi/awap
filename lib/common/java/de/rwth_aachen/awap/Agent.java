package de.rwth_aachen.awap;

import java.util.ArrayList;

public abstract class Agent {
	private byte id;
	private ArrayList<LocalService> services = new ArrayList<LocalService>();
	public AbstractNode node;

	/**
	 * will be called immediately after the constructor
	 */
	public void init(byte id, AbstractNode node) {
		this.id = id;
		this.node = node;
	}

	public byte getId() {
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

	protected void requestWakeUp(int milliseconds) {
		this.requestWakeUp(milliseconds, null);
	}


	protected void requestWakeUp(int milliseconds, Object obj) {
		this.node.requestWakeUp(milliseconds, obj);
	}

	/**
	 * This method is called when a timeout expires
	 */
	public void onWakeUp() {
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
			if(service.serviceId == msg.serviceId) {
				return service.handleMessage(msg);
			}
		}
		return false;
	}
}
