package de.rwth_aachen.awap;

import java.util.ArrayList;

import de.rwth_aachen.awap.node.IDomainFacilitator;

public abstract class LocalAgent extends Agent {
	private byte id;
	private ArrayList<ServiceProvider> services;
	private IDomainFacilitator df;

	public LocalAgent(byte id, IDomainFacilitator df) {
		this.id = id;
		this.df = df;
	}

	protected byte getId() {
		return id;
	}

	protected boolean registerService(ServiceProvider service) {
		if(this.df.registerService(service)) {
			this.services.add(service);
			return true;
		} else {
			return false;
		}
	}

	/**
	 * This method is called when the agent is installed on a node.
	 */
	public abstract void setup();
	/**
	 * This method is called when the platform is about to shut down.
	 */
	public void tearDown() {
		for(ServiceProvider service : this.services) {
			this.df.deregisterService(service);
		}
	}
}
