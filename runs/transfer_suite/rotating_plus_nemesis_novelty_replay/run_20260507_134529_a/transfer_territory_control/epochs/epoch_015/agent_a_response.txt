def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_score(x, y):
        u = 0
        o = 0
        s = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in unclaimed:
                u += 1
            if (nx, ny) in opp_terr:
                o += 1
            if (nx, ny) in self_terr:
                s += 1
        return u, o, s

    a_cnt = int(observation.get("self_territory_count", len(self_terr)) or 0)
    b_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)
    need_claim = 1 if a_cnt < b_cnt else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        val = -dist
        if (nx, ny) in resources:
            val += 6
        if (nx, ny) in unclaimed:
            val += 4 + (2 if need_claim else 0)
        if (nx, ny) in opp_terr:
            val += 12 + (4 if need_claim else 0)
        if (nx, ny) in self_terr:
            val += 2  # keep continuity to reduce vulnerability
        u, o, s = adj_score(nx, ny)
        val += 0.8 * u + 1.3 * o + 0.4 * s
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]