def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs

    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((int(x), int(y)) for x, y in opp_terr if inside(int(x), int(y)))
    my_terr = observation.get("self_territory") or []
    my_set = set((int(x), int(y)) for x, y in my_terr if inside(int(x), int(y)))

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if inside(int(x), int(y)) and not blocked(int(x), int(y)))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        if (nx, ny) in my_set:
            base = -80
        elif (nx, ny) in opp_set:
            base = 2000  # decisive flip on entry
        elif (nx, ny) in un_set:
            base = 400
        else:
            base = 0

        # Edge pressure: prioritize cells near opponent territory boundary
        edge = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in opp_set:
                    edge += 1

        # Aggress toward opponent and away from getting trapped
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_my = abs(nx - sx) + abs(ny - sy)

        # Mobility: count free neighbors
        mob = 0
        for mx, my in dirs:
            tx, ty = nx + mx, ny + my
            if inside(tx, ty) and not blocked(tx, ty):
                mob += 1

        # Slight bias to diagonals (edge claimant tends to advance diagonally)
        diag_bias = 10 if dx != 0 and dy != 0 else 0

        val = base + edge * 120 - dist_opp * 35 - dist_my * 5 + mob * 8 + diag_bias
        if val > best[1]:
            best = ([dx, dy], val)

    if best[0] is None:
        return [0, 0]
    return best[0]