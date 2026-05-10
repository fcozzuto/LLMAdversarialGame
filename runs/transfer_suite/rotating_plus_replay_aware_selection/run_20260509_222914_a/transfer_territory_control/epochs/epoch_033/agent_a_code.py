def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (sx, sy)) or (sx, sy)

    try:
        sx, sy = int(sx), int(sy)
    except Exception:
        sx, sy = 0, 0
    try:
        ox, oy = int(ox), int(oy)
    except Exception:
        ox, oy = sx, sy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                blocks.add((x, y))
    targets = []
    for key in ("unclaimed_cells", "resources"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in blocks:
                    targets.append((x, y))
        if targets:
            break
    if not targets:
        targets = [(sx, sy)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    unclaimed_bias = 0.0
    if "unclaimed_cells" in (observation or {}) and observation.get("unclaimed_cells") is not None:
        unclaimed_bias = 0.1
    cx = sx
    cy = sy
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not inside(nx, ny) or (nx, ny) in blocks:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        best_to_target = 10**9
        for tx, ty in targets[:20]:
            dd = abs(nx - tx) + abs(ny - ty)
            if dd < best_to_target:
                best_to_target = dd
        if best_to_target == 10**9:
            best_to_target = 0
        score = d_to_opp * 2 - best_to_target + (unclaimed_bias if (nx, ny) in set(observation.get("unclaimed_cells") or []) else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]