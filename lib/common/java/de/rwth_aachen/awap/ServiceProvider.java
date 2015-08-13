package de.rwth_aachen.awap;

public class ServiceProvider {
	protected LocalAgent parent;
	protected byte localServiceId;
	public ServiceProvider(LocalAgent parent) {
		this.parent = parent;
		this. localServiceId = this.parent.registerService(this);
	}
}
