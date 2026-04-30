def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b): 
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy
    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for r in resources:
            if tuple(r) in obstacles: 
                continue
            r = (r[0], r[1])
            d_self = dist2((sx, sy), r)
            d_opp = dist2((ox, oy), r)
            # Prefer resources we reach sooner than opponent; add tie-break to aim nearer.
            sc = (d_opp - d_self) * 3 - d_self
            if best is None or sc > best[0]:
                best = (sc, r)
        tx, ty = best[1] if best else (resources[0][0], resources[0][1])
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = dist2((nx, ny), (tx, ty))
        # Tie-break: keep away from opponent slightly
        do = dist2((nx, ny), (ox, oy))
        candidates.append((ds - 0.02*do, -do, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]