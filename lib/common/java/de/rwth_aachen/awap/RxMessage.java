package de.rwth_aachen.awap;

public abstract class RxMessage {
	public RemoteAgent sender;

	/**
	 * Tracks the number of retransmission attempts.
	 */
	public int retransmissions = 0;
}
