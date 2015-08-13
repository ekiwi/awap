package de.rwth_aachen.awap;

public class LocalService {
	protected Agent parent;
	protected byte localServiceId;
	public LocalService(Agent parent) {
		this.parent = parent;
		this. localServiceId = this.parent.registerService(this);
	}

	public static class Message {
		public RemoteAgent remoteAgent;
		public byte localServiceId;
	}
}
