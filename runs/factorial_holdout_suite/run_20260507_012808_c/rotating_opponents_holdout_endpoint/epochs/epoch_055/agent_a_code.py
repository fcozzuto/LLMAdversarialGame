def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # 8-neighborhood + stay, but only return moves that keep us in-bounds and not onto obstacles
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Targeting: choose move that maximizes our chance to beat the opponent at some resource,
    # with extra bias for resources that reduce distance more than the opponent.
    best = (None, -10**18)
    for dx, dy, nx, ny in candidates:
        best_cell = -10**18
        for tx, ty in resources:
            myd = manhattan((nx, ny), (tx, ty))
            opd = manhattan((ox, oy), (tx, ty))
            # Prefer resources where we are closer (smaller myd) and where opponent is farther.
            # Small tie-break toward nearer resources to keep moving decisively.
            score = (opd - myd) * 100 - myd
            if score > best_cell:
                best_cell = score
        if best_cell > best[1]:
            best = ((dx, dy), best_cell)

    return [int(best[0][0]), int(best[0][1])]