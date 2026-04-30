def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    deltas = [(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    if not resources:
        return [0, 0]
    parity = observation.get("turn_index", 0) & 1
    def dist2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy
    if parity == 0:
        target = min(resources, key=lambda r: (dist2((sx, sy), r), r[0], r[1]))
        focus = (sx, sy)
    else:
        target = min(resources, key=lambda r: (dist2((ox, oy), r), r[0], r[1]))
        focus = (ox, oy)
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        dtarget = dist2((nx, ny), target)
        dobj = dist2((nx, ny), (ox, oy))
        # minimize distance to target, maximize distance from opponent, deterministic tiebreak
        key = (dtarget, -dobj, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]