def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_ter = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_ter.add((int(p[0]), int(p[1])))

    opp_ter = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_ter.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            key = (-10**9, 0, 0, 0)
        else:
            d_center = dist(nx, ny, center[0], center[1])
            d_opp = dist(nx, ny, ox, oy)
            is_own = (nx, ny) in self_ter
            is_opp = (nx, ny) in opp_ter
            is_un = (nx, ny) in unclaimed

            # Capture opponent territory immediately if possible (entry flips control).
            cap = 1 if is_opp else 0

            # Prefer unclaimed near center; also mildly prefer moving toward opponent to create flips.
            claim = 1 if is_un else 0
            near_opp = 1 if d_opp <= 2 else 0
            own_keep = 1 if is_own else 0

            score = 0
            score += 100000 * cap
            score += 2000 * claim
            score += 40 * near_opp
            score += 8 * own_keep
            # Lower distance to center is better; higher score for smaller d_center.
            score += int(200 / (1 + d_center))
            score += int(40 / (1 + d_opp)) if claim else 0

            # Deterministic tie-breaker: fixed ordering from (dx,dy) and lex key.
            key = (score, -d_center, -d_opp, 0)

        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]