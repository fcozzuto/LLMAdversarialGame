def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valid_res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                valid_res.append((rx, ry))
    if not valid_res:
        return [0, 0]

    best = None
    best_key = None
    # Deny heuristic: prefer resources far from opponent but near us.
    # Key: maximize (opp_dist - self_dist), then prefer smaller self_dist, then parity tie-break.
    for (rx, ry) in valid_res:
        ds = man((sx, sy), (rx, ry))
        do = man((ox, oy), (rx, ry))
        v = do - ds
        parity = (rx + ry + observation.get("turn_index", 0)) & 1
        key = (v, -ds, -parity)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        ds_to = man((nx, ny), (tx, ty))
        do_from = man((nx, ny), (ox, oy))
        # Minimize distance to target; if tie, maximize distance from opponent; deterministic tie-break by dx,dy order.
        val = (ds_to, -do_from, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]