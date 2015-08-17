package de.rwth_aachen.awap;

public abstract class LocalService {
	protected Agent parent;
	public byte localServiceId;
	public LocalService(Agent parent) {
		this.parent = parent;
		this. localServiceId = this.parent.registerService(this);
	}

	public abstract boolean handleMessage(Message msg);
}
