def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obs:  # should not happen, but keep deterministic
            continue

        sd = man(nx, ny, sx, sy)
        od = man(nx, ny, ox, oy)
        advantage = od - sd  # positive means we are closer than opponent

        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0

        bonus = 0
        if (nx, ny) in self_set:
            bonus += 3
        elif (nx, ny) in un_set:
            bonus += 8
        elif (nx, ny) in opp_set:
            bonus += 6  # flipping on entry enabled

        adj = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny+1), (nx-1, ny+1), (nx+1, ny-1)]:
            if (ax, ay) in self_set:
                adj += 1

        # mild preference for reducing distance to the nearest unclaimed cell (if any)
        near_un = 0
        if un_set:
            t = man(nx, ny, *min(un_set, key=lambda p: man(nx, ny, p[0], p[1])))
            near_un = -t * 0.3

        val = advantage * 2.5 + bonus + adj * 0.6 + edge * 0.2 + near_un
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]