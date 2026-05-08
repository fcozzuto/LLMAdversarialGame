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

    def score_cell(nx, ny):
        # Aggressive counterclaim: prioritize entering opponent territory.
        if (nx, ny) in opp_terr:
            base = 5.0
        elif (nx, ny) in unclaimed:
            base = 2.0
        elif (nx, ny) in self_terr:
            base = 0.7
        else:
            base = 0.3
        # Resource attraction (small).
        if (nx, ny) in resources:
            base += 1.5
        # Stay not too close to opponent to avoid easy counter-counterclaim.
        d = abs(nx - ox) + abs(ny - oy)
        if d <= 1:
            base -= 2.0
        elif d == 2:
            base -= 1.0
        # Encourage progress toward opponent territory mass.
        if opp_terr:
            closest = 10**9
            for tx, ty in opp_terr:
                dist = abs(nx - tx) + abs(ny - ty)
                if dist < closest:
                    closest = dist
            base += 1.0 / (1.0 + closest)
        # Prefer reducing distance to opponent when actually counterclaiming adjacent.
        if (nx, ny) in opp_terr:
            base += 0.25 * (1.0 / (1.0 + abs(nx - ox) + abs(ny - oy)))
        return base

    best = None
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]