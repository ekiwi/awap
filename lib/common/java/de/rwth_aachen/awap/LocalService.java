package de.rwth_aachen.awap;

public class LocalService {
	protected Agent parent;
	public byte localServiceId;
	public LocalService(Agent parent) {
		this.parent = parent;
		this. localServiceId = this.parent.registerService(this);
	}
}
