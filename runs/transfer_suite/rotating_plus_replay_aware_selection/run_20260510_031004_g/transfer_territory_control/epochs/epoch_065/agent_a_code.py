def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - (w - 1) / 2.0) + abs(p[1] - (h - 1) / 2.0)))
    else:
        tx, ty = int((w - 1) / 2.0), int((h - 1) / 2.0)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        target_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        bonus = 0
        if (nx, ny) in unclaimed:
            bonus += 1000
        if (nx, ny) in self_terr:
            bonus += 20
        if (nx, ny) in opp_terr:
            bonus -= 50
        edge_pen = 0
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            edge_pen = -3
        # Prefer approaching target, and slightly avoid getting close to opponent
        score = bonus - target_d + (opp_d // 2) + edge_pen
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[1][0], best[1][1]]