package de.rwth_aachen.awap;

public class RemoteService {
	protected Agent parent;
	public RemoteAgent remoteAgent;
	public byte remoteServiceId;

	public RemoteService(Agent parent, RemoteAgent remoteAgent, byte remoteServiceId) {
		this.parent = parent;
		this.remoteAgent = remoteAgent;
		this.remoteServiceId = remoteServiceId;
	}
}
