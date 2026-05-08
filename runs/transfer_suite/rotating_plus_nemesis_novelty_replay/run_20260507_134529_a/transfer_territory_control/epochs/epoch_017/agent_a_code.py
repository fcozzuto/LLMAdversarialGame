def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_points(key):
        pts = observation.get(key) or []
        out = []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obstacles = set(parse_points("obstacles"))
    resources = parse_points("resources")
    unclaimed = parse_points("unclaimed_cells")
    self_terr = set(parse_points("self_territory"))
    opp_terr = set(parse_points("opponent_territory"))

    targets = resources if resources else unclaimed if unclaimed else list(self_terr)
    if not targets:
        targets = [(0, 0), (w - 1, h - 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    t0 = min(targets, key=lambda t: dist((sx, sy), t))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in resources:
            score += 40
        if (nx, ny) in opp_terr:
            score -= 35
        if (nx, ny) in self_terr:
            score += 10
        score -= dist((nx, ny), (ox, oy)) * 2
        score -= dist((nx, ny), t0)
        if best is None or score > best_score:
            best_score, best = score, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]