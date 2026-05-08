def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    opp_corner = (w - 1, h - 1)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_corner = abs(nx - opp_corner[0]) + abs(ny - opp_corner[1])

        if (nx, ny) in opp_t:
            base = 600.0
        elif (nx, ny) in unclaimed:
            base = 120.0
        elif (nx, ny) in self_t:
            base = -20.0
        else:
            base = 30.0

        # Encourage pressuring the opponent boundary; avoid wandering away.
        pressure = 0.0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in opp_t:
                    pressure += 6.0
                if (ax, ay) in unclaimed:
                    pressure += 1.0

        # Deterministic bias to reduce oscillation: prefer moving that decreases distance to opponent.
        move_towards = 10.0 if d_opp < (abs(sx - ox) + abs(sy - oy)) else -2.0

        # Prefer diagonal progress when aligned to opponent corner.
        diag = 0.0
        if dx != 0 and dy != 0:
            diag = 3.0 if (nx - sx) == (1 if opp_corner[0] > sx else -1 if opp_corner[0] < sx else 0) or (ny - sy) == (1 if opp_corner[1] > sy else -1 if opp_corner[1] < sy else 0) else 0.0

        # Soft preference for advancing toward opponent corner.
        advance = -0.35 * d_corner

        score = base + pressure + move_towards + diag + advance

        # Tie-break deterministically: prefer smaller |dx|+|dy| then fixed order
        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1] and best[0] is not None:
            cand = abs(dx) + abs(dy)
            cur = abs(best[0][0]) + abs(best[0][1])
            if cand < cur:
                best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]