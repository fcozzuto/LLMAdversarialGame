def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    selfT = set(tuple(t) for t in observation.get("self_territory") or [])
    oppT = set(tuple(t) for t in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(c) for c in observation.get("unclaimed_cells") or [])
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def score(nx, ny):
        if (nx, ny) in obstacles: return -10**9
        if nx == ox and ny == oy: return -10**8
        s = 0
        if (nx, ny) in oppT: s += 8000
        elif (nx, ny) in unclaimed: s += 260
        elif (nx, ny) in selfT: s += 60
        # Prefer pushing away from opponent while moving toward center slightly
        dist_to_op = abs(nx - ox) + abs(ny - oy)
        dist_self = abs(nx - cx) + abs(ny - cy)
        s += 3.5 * dist_to_op
        s -= 0.15 * dist_self
        # Avoid stepping adjacent to opponent (makes it easier to counterclaim)
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        if adj: s -= 180
        return s
    best = None
    best_sc = -10**18
    parity = int(observation.get("turn_index", 0) or 0) & 1
    # Deterministic tie-break: rotate preference based on parity
    order = dirs if parity == 0 else dirs[1:] + dirs[:1]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        sc = score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best