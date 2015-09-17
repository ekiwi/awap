package de.rwth_aachen.awap;

public class RemoteService {
	protected Agent parent;
	public RemoteAgent remoteAgent;
	public int serviceId;

	public RemoteService(Agent parent, RemoteAgent remoteAgent, byte serviceId) {
		this.parent = parent;
		this.remoteAgent = remoteAgent;
		this.serviceId = serviceId;
	}
}
