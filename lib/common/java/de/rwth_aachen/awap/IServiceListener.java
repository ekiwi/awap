package de.rwth_aachen.awap;

public interface IServiceListener {
	public void serviceFound(byte listenerId, int remoteAgentId);
	public void serviceRemoved(byte listenerId, int remoteAgentId);
}
