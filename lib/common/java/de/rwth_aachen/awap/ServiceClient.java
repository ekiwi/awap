package de.rwth_aachen.awap;

public abstract class ServiceClient {
	protected LocalAgent parent;
	private byte serviceId;
	public ServiceClient(LocalAgent parent, byte serviceId) {
		this.parent = parent;
	}

	public void registerListener(Property... properties) {
		this.parent.df.installServiceListener(this, this.serviceId, properties);
	}

	public abstract void serviceFound(byte listenerId, RemoteAgent remoteAgent);
	public abstract void serviceRemoved(byte listenerId, RemoteAgent remoteAgent);
}
