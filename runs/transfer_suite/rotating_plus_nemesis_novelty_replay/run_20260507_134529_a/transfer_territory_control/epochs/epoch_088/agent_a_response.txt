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
    my_neighbors = None

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_terr_list = list(opp_terr)
    opp_cent = (ox, oy)
    if opp_terr_list:
        sxm = sum(x for x, _ in opp_terr_list)
        sym = sum(y for _, y in opp_terr_list)
        opp_cent = (sxm // len(opp_terr_list), sym // len(opp_terr_list))

    directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, None)

    for dx, dy in directions:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = 0.0

        if (nx, ny) in opp_terr:
            score += 18.0
        elif (nx, ny) in unclaimed:
            score += 7.5
        elif (nx, ny) in self_terr:
            score += 2.0
        else:
            score += 1.0

        if (nx, ny) in resources:
            score += 6.0

        # Prefer expansion toward opponent-held space, but avoid leaving self_territory if already surrounded.
        score += (0.25 if (nx, ny) in self_terr else 0.0)
        score -= 0.08 * manh(nx, ny, opp_cent[0], opp_cent[1])

        # Tactical: if we can step adjacent to opponent territory, bias toward it.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in opp_terr:
                    adj = 1
        if adj:
            score += 3.5

        # Defense: discourage moving far from current territory if opponent is close.
        my_dist = manh(nx, ny, sx, sy)
        opp_dist = manh(ox, oy, nx, ny)
        score -= 0.4 * my_dist
        if opp_dist <= 2:
            score -= 2.0 if (nx, ny) not in self_terr else 0.0

        # Deterministic tie-break: lexicographic by (dx,dy) order in directions.
        key = (score, -directions.index((dx, dy)) if (dx, dy) in directions else 0, dx, dy)
        if key[0] > best[0]:
            best = (key[0], [dx, dy])

    return best[1]