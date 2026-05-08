def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_terr = []
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_terr.append((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (0, 0)
    best_val = None

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    targets = unclaimed if unclaimed else opp_terr
    if not targets:
        targets = [(w // 2, h // 2)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moving closer to nearest target; tie-breaker prefer farther from opponent
        dmin = None
        for tx, ty in targets:
            d = md(nx, ny, tx, ty)
            if dmin is None or d < dmin:
                dmin = d
        opp_d = md(nx, ny, ox, oy)
        val = (-dmin, opp_d, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]