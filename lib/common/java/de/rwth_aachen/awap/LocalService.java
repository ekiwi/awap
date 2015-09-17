package de.rwth_aachen.awap;

public abstract class LocalService {
	protected Agent parent;
	public int serviceId;
	public LocalService(Agent parent, int serviceId) {
		this.parent = parent;
		this.serviceId = serviceId;
		this.parent.registerService(this);
	}

	public abstract boolean handleMessage(Message msg);
}
