def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    resources = observation.get("resources", []) or []
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_cells.append((int(r[0]), int(r[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def step_score(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        if (nx, ny) in self_ter:
            base = 2.0
        elif (nx, ny) in opp_ter:
            base = 12.0  # capture-flip target
        elif (nx, ny) in unclaimed:
            base = 6.0   # expand
        else:
            base = 1.0
        # Prefer moving toward center / resource
        if res_cells:
            tx, ty = min(res_cells, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            center_term = -0.55 * (abs(nx - tx) + abs(ny - ty))
        else:
            center_term = -0.25 * (abs(nx - cx) + abs(ny - cy))
        # Avoid walking into opponent pressure
        opp_dist = abs(nx - ox) + abs(ny - oy)
        safety = 0.18 * opp_dist
        # Also value being adjacent to your territory (more stable expansion)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in self_ter:
                    adj += 1
        return base + center_term + safety + 0.35 * adj

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = step_score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < tuple(best_move)):
            best_val = v
            best_move = [dx, dy]
    return best_move