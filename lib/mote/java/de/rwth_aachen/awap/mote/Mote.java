package de.rwth_aachen.awap.mote;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.ServiceProperty;

public class Mote {
	public static native void send(int agentId, Message msg);
	public static native boolean deregisterService(int agentId, LocalService service);
	public static native byte installServiceListener(int agentId, Agent listener, int serviceTypeId, ServiceProperty[] properties);
	public static native boolean registerService(int agentId, LocalService service);
	public static native boolean uninstallServiceListener(int agentId, byte listenerId);
}
