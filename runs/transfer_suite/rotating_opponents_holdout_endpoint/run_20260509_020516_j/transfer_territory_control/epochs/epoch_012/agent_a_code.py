def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return 0, 0

    sx, sy = xy(observation.get("self_position", (0, 0)))
    ox, oy = xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for c in (observation.get("obstacles") or []):
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    res = set()
    for c in (observation.get("resources") or []):
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            res.add((x, y))

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            unclaimed.add((x, y))

    opp_T = set()
    for c in (observation.get("opponent_territory") or []):
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            opp_T.add((x, y))

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in res:
            score += 100000
        if (nx, ny) in unclaimed:
            score += 300
        if (nx, ny) in opp_T:
            score += 120

        d_opp = man(nx, ny, ox, oy)
        score += -2 * d_opp  # prefer approaching opponent

        if res:
            d_res = min(man(nx, ny, rx, ry) for (rx, ry) in res)
            score += -5 * d_res
        elif unclaimed:
            d_uc = min(man(nx, ny, ux, uy) for (ux, uy) in unclaimed)
            score += -2 * d_uc

        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]