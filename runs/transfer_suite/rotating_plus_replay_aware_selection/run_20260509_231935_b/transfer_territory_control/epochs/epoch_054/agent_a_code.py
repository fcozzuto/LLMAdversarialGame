def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d): 
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    dirs = dirs[t % 9:] + dirs[:t % 9]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            base = -0.2
        elif (nx, ny) in opp_terr:
            base = 6.0
        elif (nx, ny) in unclaimed:
            base = 3.5
        else:
            base = 0.0

        d_opp = man(nx, ny, ox, oy)
        d_ctr = man(nx, ny, cx, cy)

        near_uncl = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if inside(ax, ay) and (ax, ay) in unclaimed:
                near_uncl += 1

        in_opp_front = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if inside(ax, ay) and (ax, ay) in opp_terr:
                in_opp_front += 1

        # Prefer conquering nearby unclaimed and pressuring opponent while moving toward center
        score = base + 0.6 * near_uncl + 0.9 * in_opp_front - 0.08 * d_ctr - 0.03 * d_opp
        if best is None or score > best[0] or (score == best[0] and (dx, dy) == (0, 0)):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]