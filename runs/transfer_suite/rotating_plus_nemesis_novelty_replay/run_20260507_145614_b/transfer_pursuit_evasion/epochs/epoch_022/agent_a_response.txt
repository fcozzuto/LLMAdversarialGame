def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("escape" in self_role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    if not is_evader:
        cx, cy = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Bias toward corner (helps stability vs wall-running), and avoid getting into "tight" obstacle neighborhoods.
        corner_d2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        neigh_free = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    neigh_free += 1
        # Score: evader wants larger distance and corner_d2 (to go "away"), pursuer wants smaller distance and corner_d2 (to go "toward").
        score = d2 - 0.15 * corner_d2 + 0.05 * neigh_free if is_evader else -d2 - 0.15 * corner_d2 + 0.05 * neigh_free
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]