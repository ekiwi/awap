package de.rwth_aachen.awap.node;

import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.RemoteService;

public interface ICommunication {
	/**
	 * Send a message to a service located on a different agent.
	 * @param msg
	 */
	public void send(RemoteService.Message msg);
	/**
	 * send a message from a service located on this agent to a remote agent.
	 * @param msg
	 */
	public void send(LocalService.Message msg);
}
