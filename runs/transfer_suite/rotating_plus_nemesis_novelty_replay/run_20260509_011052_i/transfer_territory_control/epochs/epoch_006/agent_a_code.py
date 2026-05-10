def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    self_count = observation.get("self_territory_count", len(self_terr))
    want_flip = 1 if opp_count > self_count else 0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -1e18

    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 7.0
        if (nx, ny) in self_terr:
            score += 1.0
        if (nx, ny) in opp_terr:
            score += 4.5 + 3.0 * want_flip

        score += 0.2 * (-abs(nx - center_x) - abs(ny - center_y))
        score += 0.35 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]