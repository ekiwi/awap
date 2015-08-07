package de.rwth_aachen.awap.node;

import de.rwth_aachen.awap.TxMessage;

public interface ICommunication {
	public void send(TxMessage msg);
}
