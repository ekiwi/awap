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

	protected void registerTimeout(int milliseconds) {
		this.registerTimeout(milliseconds, null);
	}


	protected void registerTimeout(int milliseconds, Object obj) {

	}

	/**
	 * This method is called when a timeout expires
	 */
	public abstract void onWakeUp();

	/**
	 * This method is called when the platform is about to shut down.
	 */
	public void tearDown() {
		for(LocalService service : this.services) {
			this.node.deregisterService(service);
		}
	}

	public boolean handleLocalServiceMessage(Message msg) {
		if(msg.remoteService) {
			// cannot handle message from remote service
			// these have to be delivered to the agent from
			// the outside, by traying to cast it to the
			// associated interface
			return false;
		} else {
			// service is local service on this agent
			try {
				return this.services.get(msg.serviceId).handleMessage(msg);
			} catch (IndexOutOfBoundsException e) {
				return false;
			}

		}
	}
}
