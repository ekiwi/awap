/**
 * AgentRegistry.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


package de.rwth_aachen.awap.jade;

import jade.core.AID;

import java.util.HashMap;

/**
 * Manages the LocalAgent.id <-> AID mappings.
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public final class AgentRegistry {
	private static HashMap<AID, Integer> aidMapping = new HashMap<AID, Integer>();
	private static HashMap<Integer, AID> idMapping = new HashMap<Integer, AID>();

	public static int getId(AID aid) {
		if(!aidMapping.containsKey(aid)) {
			int id = newId();
			aidMapping.put(aid, id);
			idMapping.put(id, aid);
		}
		return aidMapping.get(aid);
	}

	public static AID getId(int id) {
		return idMapping.get(id);
	}


	private static int newId() {
		int id = 0;
		while(idMapping.containsKey(id)) {
			id++;
		}
		return id;
	}
}
