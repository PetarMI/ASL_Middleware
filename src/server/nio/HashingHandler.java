package server.nio;

import java.util.Collection;
import java.util.SortedMap;
import java.util.TreeMap;

public class HashingHandler<T> {

	private static final int NUM_REPLICAS = 10000;
	private final HashFunction hashFunction;
	private final SortedMap<Long, T> circle = new TreeMap<Long, T>();
	
	public HashingHandler(Collection<T> nodes) {
		this.hashFunction = new HashFunction();
	
		for (T node : nodes) {
			this.add(node);
		}
		
		System.out.println("Number of points" + circle.size());
	}
	
	public T get(String key) {
		if (circle.isEmpty()) {
			return null;
		}
	  
		Long hash = hashFunction.hash(key);
		if (!circle.containsKey(hash)) {
			SortedMap<Long, T> tailMap = circle.tailMap(hash);
			hash = tailMap.isEmpty() ? circle.firstKey() : tailMap.firstKey();
		}
		return circle.get(hash);
	}
	
	public void add(T node) {
		for (int i = 0; i < NUM_REPLICAS; i++) {
			Long  point = hashFunction.hash(node.toString() + i);
			circle.put(point, node);
			//System.out.println(point);
		}
		//System.out.println();
	}

	public void remove(T node) {
		for (int i = 0; i < NUM_REPLICAS; i++) {
			circle.remove(hashFunction.hash(node.toString() + i));
		}
	}
}