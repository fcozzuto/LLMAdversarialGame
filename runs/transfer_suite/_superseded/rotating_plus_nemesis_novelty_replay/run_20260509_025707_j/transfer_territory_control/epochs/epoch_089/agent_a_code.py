def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((p[0], p[1]))
    resources = [(p[0], p[1]) for p in (observation.get("resources") or [])]
    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])]

    candidates = resources if (observation.get("remaining_resource_count", len(resources)) or 0) > 0 and resources else unclaimed
    if not candidates:
        candidates = [(sx, sy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_opp = abs(nx - ox) + abs(ny - oy)
        close_pen = 50 if dist_opp <= 1 else 0
        best_dist = 10**9
        for tx, ty in candidates:
            d = abs(nx - tx) + abs(ny - ty)
            if d < best_dist:
                best_dist = d
        edge = 2 if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1 else 0
        score = (-best_dist) - close_pen + edge
        if score > best[0] or (score == best[0] and (dx, dy) > (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]] if inb(sx + best[1], sy + best[2]) else [0, 0]