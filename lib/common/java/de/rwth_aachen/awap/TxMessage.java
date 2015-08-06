package de.rwth_aachen.awap;

public abstract class TxMessage {
	public Agent receiver;

	/**
	 * Tracks the number of retransmission attempts.
	 */
	public int retransmissions = 0;
}
