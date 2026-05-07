def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Light obstacle-aware tie-break: prefer moves whose next cells have fewer adjacent obstacles
    def adj_obst_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    # Choose a target using opponent denier logic + diagonal metric
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If opponent is closer, prioritize resources that are "safe" (we can reach not slower)
        safe = 1 if od <= sd else 0
        # Score favors: winning race to resource, then bigger race advantage, then closer by our metric
        key = (
            0 if od <= sd else 1,                 # prefer od<=sd
            -(od - sd),                          # larger advantage
            -safe,                               
            sd,                                   # nearer to us
            (rx + 7 * ry)                        # deterministic final tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Move one step toward target with deterministic diagonal preference:
    # evaluate all legal deltas and pick best by (distance-to-target, next-cell obstacle adjacency, x then y)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        candidates.append((nd, adj_obst_count(nx, ny), dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    dx, dy = candidates[0][2], candidates[0][3]
    return [dx, dy]