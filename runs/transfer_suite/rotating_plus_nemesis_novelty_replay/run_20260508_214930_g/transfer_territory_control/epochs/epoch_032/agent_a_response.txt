def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_score(x, y):
        c_self = 0
        c_opp = 0
        c_un = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not inside(nx, ny):
                    continue
                if (nx, ny) in self_t:
                    c_self += 1
                if (nx, ny) in opp_t:
                    c_opp += 1
                if (nx, ny) in unclaimed:
                    c_un += 1
        return c_self, c_opp, c_un

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 3.0
        if (nx, ny) in opp_t:
            base += 6.0
        if (nx, ny) in self_t:
            base -= 0.2

        c_self, c_opp, c_un = adj_score(nx, ny)
        sc = base + 0.6 * c_un + 0.25 * c_self - 0.35 * c_opp
        # If we're about to challenge, prefer making contact over idle expansion
        if c_opp > 0 and (nx, ny) not in self_t:
            sc += 0.7

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]