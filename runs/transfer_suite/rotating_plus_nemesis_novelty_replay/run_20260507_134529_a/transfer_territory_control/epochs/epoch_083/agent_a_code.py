def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_cell(nx, ny):
        if (nx, ny) in opp_terr:
            base = 6.0
        elif (nx, ny) in unclaimed:
            base = 2.6
        elif (nx, ny) in self_terr:
            base = 0.6
        else:
            base = 0.2
        if (nx, ny) in resources:
            base += 1.8
        # Prefer progress away from our corner toward center slightly (reduces getting stuck).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        base += 0.15 * (-(abs(nx - cx) + abs(ny - cy)))
        # Penalize moving close to opponent unless we are entering their territory (capture priority).
        dist_opp = max(0, manh(nx, ny, ox, oy) - 0)
        if (nx, ny) not in opp_terr:
            base -= 0.35 / (1 + dist_opp)
        return base

    best = None
    best_sc = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # Tie-break: closer to opponent territory centroid; otherwise closer to any high-value cell.
        if opp_terr:
            tx = sum(x for x, y in opp_terr) / len(opp_terr)
            ty = sum(y for x, y in opp_terr) / len(opp_terr)
            sc -= 0.01 * (abs(nx - tx) + abs(ny - ty))
        else:
            if unclaimed:
                ux, uy = min(unclaimed, key=lambda p: manh(nx, ny, p[0], p[1]))
                sc -= 0.01 * manh(nx, ny, ux, uy)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best