package de.rwth_aachen.awap;

import java.util.ArrayList;

import de.rwth_aachen.awap.node.AbstractNode;
import de.rwth_aachen.awap.node.ICommunication;
import de.rwth_aachen.awap.node.IDomainFacilitator;
import de.rwth_aachen.awap.node.IHardware;

public abstract class Agent {
	private byte id;
	private ArrayList<LocalService> services;
	IDomainFacilitator df;
	public ICommunication com;
	IHardware hw;

	public Agent(byte id, AbstractNode node) {
		this.id = id;
		this.df = node;
		this.com = node;
		this.hw = node;
		this.services = new ArrayList<LocalService>();
	}

	public byte getId() {
		return id;
	}

	protected byte registerService(LocalService service) {
		if(this.df.registerService(service)) {
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

	/**
	 * This method is called when the platform is about to shut down.
	 */
	public void tearDown() {
		for(LocalService service : this.services) {
			this.df.deregisterService(service);
		}
	}
}
