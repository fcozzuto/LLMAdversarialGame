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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    best = None
    best_score = -1e18
    cur_opp_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        # Edge-control bias: grab frontier near opponent territory.
        frontier = 0.0
        if cell in opp_terr:
            frontier += 8.0
        if cell in unclaimed:
            frontier += 3.2 if adj_opp(nx, ny) else 1.2
        if cell in self_terr:
            frontier += 1.0 if adj_opp(nx, ny) else 0.4

        # Defensive spacing: avoid giving easy recapture by staying closer to center line.
        nd = abs(nx - ox) + abs(ny - oy)
        spacing = (nd - cur_opp_dist) * 0.15  # prefer not to approach too much

        # Resource micro-bonus.
        res = 0.0
        if cell in resources:
            res += 3.5
        else:
            # small deterministic pull toward nearest resource without search
            if resources:
                min_rd = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
                res += 1.2 / (1 + min_rd)

        # Tie-break toward unclaimed / non-self cells; prefer staying deterministic.
        self_pen = -0.2 if cell in self_terr else 0.0
        opp_pen = -0.1 if cell in opp_terr else 0.0

        score = frontier + spacing + res + self_pen + opp_pen

        if score > best_score + 1e-9:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]