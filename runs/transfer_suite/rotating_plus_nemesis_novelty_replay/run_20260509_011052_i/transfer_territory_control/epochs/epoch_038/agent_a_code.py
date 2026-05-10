def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    best = None
    bestv = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine will keep in place if invalid
        is_opp = (nx, ny) in opp_terr
        is_uncl = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_terr
        d_opp = abs(nx - ox) + abs(ny - oy)
        v = 0.0
        v += 6.0 if is_opp else 0.0
        v += 1.6 if is_uncl else 0.0
        v += 0.3 if is_self else 0.0
        v += 0.15 * adj_count(nx, ny, self_terr)
        v -= 0.20 * adj_count(nx, ny, opp_terr)
        v += 0.02 * d_opp  # prefer staying away from opponent while expanding
        v -= 0.01 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))  # mild drive toward upper-right/near-opponent side
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best