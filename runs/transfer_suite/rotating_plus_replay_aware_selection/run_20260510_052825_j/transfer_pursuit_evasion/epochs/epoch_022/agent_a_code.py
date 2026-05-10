def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = ("evad" in self_role) or (self_role == "evader")
    is_pursuer = ("purs" in self_role) or (self_role == "pursuer")
    if is_evader:
        mode = "evade"
    elif is_pursuer:
        mode = "pursue"
    else:
        mode = "pursue" if (("evad" in opponent_role) or ("evader" == opponent_role)) else "evade"

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    dirs4 = [(-1,0),(1,0),(0,-1),(0,1)]
    def score(x, y):
        dpx = x - ox; dpy = y - oy
        d2 = dpx*dpx + dpy*dpy
        adj = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                adj += 1
        pen = adj
        if mode == "evade":
            return d2 - 0.7*pen
        return -d2 - 0.7*pen

    best = None
    best_sc = None
    for dx, dy in deltas:
        x, y = sx + dx, sy + dy
        if not free(x, y):
            continue
        sc = score(x, y)
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in deltas:
            x, y = sx + dx, sy + dy
            if inb(x, y) and (x, y) in obs:
                continue
            if inb(x, y):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]