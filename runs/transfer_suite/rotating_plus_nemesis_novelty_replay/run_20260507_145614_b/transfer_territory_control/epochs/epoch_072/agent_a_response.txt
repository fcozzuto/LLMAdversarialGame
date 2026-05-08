def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_set = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    self_set = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in opp_set:
                        return True
        return False

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # 1) If we can step onto opponent territory, do it (deterministic best landing).
    best_land = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) in opp_set:
                score = (0, abs(nx - ox) + abs(ny - oy), nx, ny)
                if best_land is None or score < best_land:
                    best_land = (dx, dy)
    if best_land is not None:
        return [best_land[0], best_land[1]]

    # 2) Pick target unclaimed: prioritize cells adjacent to opponent, then edge, then closer.
    if not unclaimed:
        return [0, 0]
    best = None
    for x, y in unclaimed:
        if (x, y) in self_set:
            continue
        edge = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
        near_opp = adj_to_opp(x, y)
        pri = (0 if near_opp else 1, 0 if edge else 1, dist(sx, sy, x, y), x, y)
        if best is None or pri < best:
            best = (x, y)
    tx, ty = best

    # 3) Choose a step that avoids obstacles and reduces distance to target; deterministic tie-break.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = dist(nx, ny, tx, ty)
                # Prefer moves that also move closer to opponent territory boundary.
                boundary = 0
                if adj_to_opp(nx, ny):
                    boundary = -3
                candidates.append(((d + boundary), abs(dx) + abs(dy), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [dx, dy]