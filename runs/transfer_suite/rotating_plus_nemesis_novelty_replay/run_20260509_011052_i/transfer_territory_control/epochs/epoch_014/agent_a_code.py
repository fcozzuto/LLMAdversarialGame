def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def near_obst_pen(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    p += 1
        return p

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0.0
        dcen = abs(nx - cx) + abs(ny - cy)
        if (nx, ny) in opp_terr:
            val += 8.0
        elif (nx, ny) in unclaimed:
            val += 5.0
        elif (nx, ny) in self_terr:
            val += 2.0
        if (nx, ny) not in self_terr:
            val += 1.0
        val += (14.0 - dcen) * 0.25  # prefer interior control
        # avoid running to opponent when grabbing isn't immediate
        dopp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) not in opp_terr:
            val -= dopp * 0.02
        val -= near_obst_pen(nx, ny) * 0.35
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]