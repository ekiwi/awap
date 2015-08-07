package de.rwth_aachen.awap;

public class ServiceProvider {
	protected LocalAgent parent;
	public ServiceProvider(LocalAgent parent) {
		this.parent = parent;
		this.parent.registerService(this);
	}
}
