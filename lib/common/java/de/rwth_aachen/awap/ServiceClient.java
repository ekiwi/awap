package de.rwth_aachen.awap;

public abstract class ServiceClient {
	protected LocalAgent parent;
	public ServiceClient(LocalAgent parent) {
		this.parent = parent;
	}

	public void registerListener(Property... properties) {
		this.parent.df.installServiceListener(this, properties);
	}

	public abstract void serviceFound(byte listenerId, RemoteAgent remoteAgent);
	public abstract void serviceRemoved(byte listenerId, RemoteAgent remoteAgent);
}
