package de.rwth_aachen.awap;

public abstract class TxMessage {
	public RemoteAgent receiver;
	public LocalAgent sender;

	/**
	 * Tracks the number of retransmission attempts.
	 */
	public int retransmissions = 0;
}
