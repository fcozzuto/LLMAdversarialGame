def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**9

    def adj_opp_count(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in opp_t:
                    c += 1
        return c

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            sc = -10**8
        else:
            sc = 0
            if (nx, ny) in unclaimed:
                sc += 4
            if (nx, ny) in opp_t:
                sc += 8  # flipping into opponent territory is valuable
            if (nx, ny) in self_t:
                sc -= 2  # avoid just expanding nowhere
            sc += adj_opp_count(nx, ny) * 1.0  # pressure against opponent frontier
            sc -= (abs(nx - ox) + abs(ny - oy)) * 0.05  # slightly prefer closing
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]