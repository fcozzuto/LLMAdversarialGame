def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b): 
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy

    if not resources:
        # Move toward center while keeping distance from opponent
        cx, cy = (w-1)/2.0, (h-1)/2.0
        best = None
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            val = dist2((nx, ny), (cx, cy)) * (-1) + dist2((nx, ny), (ox, oy))
            if val > best_val:
                best_val = val; best = [dx, dy]
        return best if best is not None else [0, 0]

    best = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the single best target resource for this candidate (closest to us)
        best_self = 10**18
        chosen = None
        for r in resources:
            d = dist2((nx, ny), r)
            if d < best_self:
                best_self = d; chosen = r

        # If tied, prefer the resource that keeps us ahead of opponent
        if chosen is None:
            continue
        opp_d = dist2((ox, oy), chosen)
        # Primary: minimize our distance; Secondary: maximize opponent distance to our target
        val = (-best_self) + 0.7 * opp_d

        # Small tie-break: prefer moving closer to center
        cx, cy = (w-1)/2.0, (h-1)/2.0
        val += -0.01 * dist2((nx, ny), (cx, cy))

        if val > best_val:
            best_val = val; best = [dx, dy]

    # If all moves invalid, stay
    return best if best is not None else [0, 0]