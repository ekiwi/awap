package de.rwth_aachen.awap;

public class RemoteService {
	protected Agent parent;
	public RemoteAgent remoteAgentId;
	public byte remoteServiceId;

	public static class Message {
		public RemoteService service;
	}
}