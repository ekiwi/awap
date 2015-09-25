/**
 * ServiceFilter.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

import java.util.ArrayList;

public class ServiceFilter {
	public int serviceId;
	public ArrayList<ServiceProperty> properties;

	public ServiceFilter(int serviceId) {
		this.serviceId = serviceId;
		this.properties = new ArrayList<ServiceProperty>();
	}
}
