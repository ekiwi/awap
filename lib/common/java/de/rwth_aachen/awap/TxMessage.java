package de.rwth_aachen.awap;

public abstract class TxMessage {
	public RemoteAgent receiver;
	// invalid if value is -1
	public byte remoteServiceId = -1;
	// invalid if value is -1
	public byte localServiceId = -1;

	/**
	 * Tracks the number of retransmission attempts.
	 */
	public int retransmissions = 0;
}
