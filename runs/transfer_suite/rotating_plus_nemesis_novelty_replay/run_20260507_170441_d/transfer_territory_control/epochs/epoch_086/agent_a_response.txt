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

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    d0 = man(sx, sy, ox, oy)
    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue

        sc = 0.0
        in_opp = (nx, ny) in opp_t
        in_self = (nx, ny) in self_t
        in_un = (nx, ny) in unclaimed

        if in_opp:
            sc += 10.0 + 0.1 * man(nx, ny, ox, oy)
        if in_un:
            sc += 3.0
        if in_self:
            sc += 0.3

        d1 = man(nx, ny, ox, oy)
        sc += 1.2 * (d0 - d1)  # move toward opponent
        sc += -0.02 * (abs(nx - cx) + abs(ny - cy))  # slight center control
        sc += 0.001 * (nx * 31 + ny)  # deterministic tie-breaker component

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]