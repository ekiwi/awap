package de.rwth_aachen.awap;

public abstract class LocalService {
	protected Agent parent;
	public int serviceTypeId;
	public LocalService(Agent parent, int serviceTypeId) {
		this.parent = parent;
		this.serviceTypeId = serviceTypeId;
		this.parent.registerService(this);
	}

	public abstract boolean handleMessage(Message msg);
}
