def choose_move(observation):
    # Defensive extraction with .get, defaulting to safe values
    shape = observation.get('shape', (0, 0))
    my_pos = observation.get('current_player', {}).get('position', (0, 0))
    own_id = observation.get('current_player', {}).get('id', None)
    obj_list = observation.get('objects', [])
    
    # Helper to find objects by type
    def find_objects(obj_type):
        return [obj for obj in obj_list if obj.get('type') == obj_type]
    
    # Helper to find neighbor objects
    def neighbors():
        nx, ny = my_pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor_x = nx + dx
                neighbor_y = ny + dy
                # Check bounds
                if 0 <= neighbor_x < shape[0] and 0 <= neighbor_y < shape[1]:
                    yield (dx, dy), neighbor_x, neighbor_y
    
    # Prioritize based on common objectives: resource collection, evasion, territory
    # 1. Resource collection
    resource_objs = find_objects('resource')
    if resource_objs:
        # Find nearest resource
        min_dist = float('inf')
        move = (0, 0)
        for (dx, dy), nx, ny in neighbors():
            for res in resource_objs:
                res_x, res_y = res.get('position', (0,0))
                dist = abs(res_x - (my_pos[0] + dx)) + abs(res_y - (my_pos[1] + dy))
                if dist < min_dist:
                    min_dist = dist
                    move = (dx, dy)
        if move != (0, 0):
            return list(move)
        # If no better move, fall through to other strategies
    
    # 2. Evasion from opponents (simple avoidance)
    opponent_objs = [obj for obj in obj_list if obj.get('type') == 'opponent']
    threat_neighbors = []
    for (dx, dy), nx, ny in neighbors():
        for opp in opponent_objs:
            opp_x, opp_y = opp.get('position', (0,0))
            if opp_x == nx and opp_y == ny:
                threat_neighbors.append((dx, dy))
    if threat_neighbors:
        # Move away from threats if possible
        # Evaluate directions that are not threatened
        safe_moves = [(dx, dy) for (dx, dy) in [(-1,0),(1,0),(0,-1),(0,1)]]
        for move in safe_moves:
            if move not in threat_neighbors:
                return list(move)
        # If surrounded, wait or pick any move
        return [0, 0]
    
    # 3. Territory control attempt: move to less occupied neighbor
    # Count objects in neighboring cells
    neighbor_counts = []
    for (dx, dy), nx, ny in neighbors():
        count = 0
        for obj in obj_list:
            obj_x, obj_y = obj.get('position', (0,0))
            if obj_x == nx and obj_y == ny:
                count += 1
        neighbor_counts.append(((dx, dy), count))
    # Choose neighbor with fewest objects
    min_count = min(count for _, count in neighbor_counts) if neighbor_counts else 0
    for (dx, dy), count in neighbor_counts:
        if count == min_count:
            return [dx, dy]
    
    # Default: stay in place
    return [0, 0]
