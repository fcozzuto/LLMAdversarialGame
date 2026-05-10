def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    t = int(observation.get("turn_index", 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    leader_mode = (t % 10 == 0 and int(observation.get("self_territory_count", 0)) >= int(observation.get("opponent_territory_count", 0)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = [0, 0]
    bestv = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_set:
            v = 0.8
        elif (nx, ny) in opp_set:
            v = 6.0
        elif (nx, ny) in un_set:
            v = 3.0
        else:
            v = 1.0

        if leader_mode:
            v += 0.4
            v += 0.02 * (w * h - man(nx, ny, ox, oy))  # drift toward opponent while leading

        # Prefer progressing into the center and away from our own edge
        v += 0.04 * (-man(nx, ny, cx, cy))

        # Prefer steps that reduce distance to the nearest unclaimed cell
        # (cheap approximation: compare a few candidates by directional reduction)
        if un_set:
            # deterministic directional bias based on relative position to center and to opp
            dcenter = man(nx, ny, cx, cy)
            dop = man(nx, ny, ox, oy)
            v += 0.15 * (1.0 / (1.0 + dcenter)) + 0.08 * (1.0 / (1.0 + dop))

        # Avoid oscillatory bias by slightly penalizing moves that go back toward current opposite corner
        corner_bias = man(nx, ny, w - 1 - sx, h - 1 - sy)
        v += -0.005 * corner_bias

        # Deterministic tie-break: lexicographically smaller (dx,dy) after score
        if v > bestv or (v == bestv and (dx, dy) < (best_dxdy[0], best_dxdy[1])):
            bestv = v
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]