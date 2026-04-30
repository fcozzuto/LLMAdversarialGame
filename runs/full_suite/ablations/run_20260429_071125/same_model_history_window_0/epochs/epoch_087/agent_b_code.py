def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = observation["obstacles"]
    ox_set = set((p[0], p[1]) for p in obstacles)
    deltas = [(0,0),(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a,b,c,d):
        dx = abs(a-c); dy = abs(b-d)
        return dx if dx>dy else dy
    if not resources:
        return [0, 0]
    # Pick a resource we can secure (closer than opponent, but not too far for us)
    best = None; best_val = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        val = (ds - 0.9 * do) + 0.01 * (rx + 3 * ry)  # deterministic tie-break
        if best_val is None or val < best_val:
            best_val = val; best = (rx, ry)
    tx, ty = best
    # If on target resource, stay to collect
    if sx == tx and sy == ty:
        return [0, 0]
    # Choose safe move that most reduces distance to target; also tries to increase opponent distance
    best_move = (0, 0); best_t = None; best_o = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in ox_set:
            continue
        td = dist(nx, ny, tx, ty)
        od = dist(nx, ny, ox, oy)
        if best_t is None or td < best_t or (td == best_t and (best_o is None or od > best_o)) or (td == best_t and od == best_o and (dx, dy) < best_move):
            best_t = td; best_o = od; best_move = (dx, dy)
    # If all moves blocked, stay
    return [int(best_move[0]), int(best_move[1])]