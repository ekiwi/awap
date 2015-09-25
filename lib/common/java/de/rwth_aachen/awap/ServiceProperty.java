/**
 * ServiceProperty.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public class ServiceProperty {
	public int propertyId;
	public int value;

	public ServiceProperty(int id, int value) {
		this.propertyId = id;
		this.value = value;
	}
}
