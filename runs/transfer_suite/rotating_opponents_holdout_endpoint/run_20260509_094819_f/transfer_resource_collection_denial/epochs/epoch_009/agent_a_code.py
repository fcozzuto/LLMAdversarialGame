def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if resources:
        # pick nearest resource by Manhattan; deterministic tie-break by (x,y)
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if not valid(tx, ty):
                    continue
                d = abs(sx - tx) + abs(sy - ty)
                key = (d, tx, ty)
                if best is None or key < best[0]:
                    best = (key, (tx, ty))
        if best is not None:
            tx, ty = best[1]
            candidates = []
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    nd = abs(nx - tx) + abs(ny - ty)
                    # small deterministic preference to avoid staying still
                    stay_pen = 1 if (dx == 0 and dy == 0) else 0
                    candidates.append((nd + stay_pen, dx, dy))
            if candidates:
                candidates.sort()
                return [candidates[0][1], candidates[0][2]]

    # fallback: move toward center, then opponent, avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    tx, ty = (cx, cy) if (sx != cx or sy != cy) else (ox, oy)
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d = abs(nx - tx) + abs(ny - ty)
            candidates.append((d, dx, dy))
    candidates.sort()
    if candidates:
        return [candidates[0][1], candidates[0][2]]
    return [0, 0]