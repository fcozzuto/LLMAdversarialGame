def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    for k in ("resources", "unclaimed_cells"):
        v = observation.get(k)
        if v:
            for p in v:
                if p and len(p) >= 2:
                    targets.append((int(p[0]), int(p[1])))
            if targets:
                break

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score(nx, ny):
        if targets:
            t = min(targets, key=lambda p: man((nx, ny), p))
            d_t = man((nx, ny), t)
            pref = 1000 - d_t
        else:
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            d_t = abs(nx - cx) + abs(ny - cy)
            pref = 500 - d_t
        d_o = man((nx, ny), (ox, oy))
        safety = d_o * 5
        return pref + safety

    best = None
    best_sc = -10**18
    for dx, dy, nx, ny in cand:
        sc = score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]