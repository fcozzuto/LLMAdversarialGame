def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_set = {(x, y) for x, y in (observation.get("obstacles") or [])}
    opp_set = {(x, y) for x, y in (observation.get("opponent_territory") or [])}
    unclaimed = [(x, y) for x, y in (observation.get("unclaimed_cells") or [])]
    un_set = set(unclaimed)

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def manhattan(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    if unclaimed:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = min(unclaimed, key=lambda p: (manhattan(p[0], p[1], cx, cy), manhattan(p[0], p[1], sx, sy)))
    else:
        target = (ox, oy)

    tx, ty = target
    best = [0, 0]
    best_score = -10**18

    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_set:
            score += 2000  # strong immediate counterclaim
        if (nx, ny) in un_set:
            score += 200   # expand into neutral territory
        if (nx, ny) == (tx, ty):
            score += 50

        # Prefer reducing distance to the chosen target; mildly punish approaching opponent too much
        score -= manhattan(nx, ny, tx, ty)
        score += 0.15 * manhattan(nx, ny, ox, oy)

        # If moving into opponent territory, prefer positions that are farther from them afterward
        if (nx, ny) in opp_set:
            score += 0.05 * manhattan(nx, ny, ox, oy)

        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return best