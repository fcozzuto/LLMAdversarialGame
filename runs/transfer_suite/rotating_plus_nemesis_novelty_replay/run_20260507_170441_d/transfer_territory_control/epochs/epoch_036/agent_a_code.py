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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 1700
            v += 15 * (8 - min(8, man(nx, ny, ox, oy)))  # prefer capturing nearer the sweeper
        elif (nx, ny) in unclaimed:
            v += 520
        elif (nx, ny) in self_t:
            v += 90

        v += 220 - 14 * man(nx, ny, ox, oy)  # keep distance from opponent
        v -= int((abs(nx - cx) + abs(ny - cy)) * 4)  # drift toward center (safer expansion)

        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in blocked:
                    adj_obs += 1
        v -= adj_obs * 35

        if v > best[0]:
            best = (v, dx, dy)

    return [int(best[1]), int(best[2])]