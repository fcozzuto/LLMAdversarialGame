def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not unclaimed and not opp_terr:
        return [0, 0]

    # Deterministically choose a "safe" target: prefer cells we are closer to than opponent.
    targets = list(unclaimed if unclaimed else opp_terr)
    targets.sort(key=lambda p: (p[0], p[1]))
    targets = targets[:30] if len(targets) > 30 else targets

    best = None
    best_key = None
    for tx, ty in targets:
        if (tx, ty) in obstacles:
            continue
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        advantage = do - ds  # positive means we are closer
        # Prefer expanding near our current territory; otherwise nearby cells.
        if self_terr:
            df = min(abs(tx - fx) + abs(ty - fy) for (fx, fy) in self_terr)
        else:
            df = ds
        # tie-break deterministically to avoid oscillation
        key = (advantage, -df, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Candidate next positions from current (including stay), deterministic order.
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    moves.sort(key=lambda m: (abs(m[0]) + abs(m[1]), m[0], m[1]))
    next_candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid stepping into opponent territory unless no alternatives reduce distance.
        step_into_opp = (nx, ny) in opp_terr
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        # Prefer non-opponent cells; then reduce distance.
        penalty = 1000 if step_into_opp else 0
        next_candidates.append((penalty + dist_to_target, penalty, dist_to_target, nx, ny))
    if not next_candidates:
        return [0, 0]
    next_candidates.sort()
    _, _, _, nx, ny = next_candidates[0]
    return [nx - sx, ny - sy]