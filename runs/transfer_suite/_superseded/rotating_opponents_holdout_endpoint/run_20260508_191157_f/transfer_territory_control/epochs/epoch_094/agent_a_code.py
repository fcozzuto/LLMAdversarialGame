def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    stc = int(observation.get("self_territory_count") or 0)
    otc = int(observation.get("opponent_territory_count") or 0)
    attack = stc < otc

    if resources:
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    else:
        tx, ty = (ox, oy) if attack else (cx, cy)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        md = abs(nx - tx) + abs(ny - ty)
        mo = abs(nx - ox) + abs(ny - oy)
        onto = 1 if (nx, ny) in set(resources) else 0
        score = (-md) + (0.5 * mo if not attack else -0.1 * mo) + (1000 if onto else 0)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]