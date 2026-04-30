def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    res = set((p[0], p[1]) for p in resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            return sx, sy
        return nx, ny
    def d2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    opp_next = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not legal(nx, ny):
            nx, ny = ox, oy
        opp_next.append((nx, ny))
    opp_next = list(dict.fromkeys(opp_next))

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = clamp_move(dx, dy)
        if (nx, ny) in res:
            return [dx, dy]

        worst = 10**18
        for ax, ay in opp_next:
            if ax == nx and ay == ny:
                s = -10**7
            else:
                s = 0
                for rx, ry in resources:
                    myd = d2(nx, ny, rx, ry)
                    opd = d2(ax, ay, rx, ry)
                    # Prefer being closer; penalize giving opponent advantage.
                    if myd == 0: s += 10**6
                    s += (opd - myd)
                # Encourage moving toward nearest resource in our direction
                if resources:
                    mn = 10**18
                    for rx, ry in resources:
                        dd = d2(nx, ny, rx, ry)
                        if dd < mn: mn = dd
                    s -= mn * 0.001
            if s < worst: worst = s
        if worst > best[0]:
            best = (worst, dx, dy)

    return [best[1], best[2]]