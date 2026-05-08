def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 7, 7

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    occupied = self_t | opp_t
    opp_list = list(opp_t) if opp_t else [(ox, oy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_sc = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            # Prefer claiming unclaimed cells, but keep away from opponent (edge-claim deterrence).
            min_opp_d = 10**9
            for (px, py) in opp_list:
                d = man(nx, ny, px, py)
                if d < min_opp_d:
                    min_opp_d = d
            sc = min_opp_d * 50
            if (nx, ny) in self_t:
                sc += 5
            elif (nx, ny) in opp_t:
                sc += 10  # flipping on entry: acceptable if it still keeps distance
            else:
                sc += 40  # unclaimed territory likely

            # Obstacle proximity penalty (encourage corridors away from blockers).
            for ddx, ddy in dirs:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) in obstacles:
                    sc -= 7

            # Slight preference for advancing toward the center to reduce predictable edge grabs.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = abs(nx - cx) + abs(ny - cy)
            sc -= int(dist_center * 2)

            # Deterministic tie-break: prefer staying closer to our current position.
            sc -= (abs(dx) + abs(dy))

            # If we can directly step onto opponent, give a small deterministic bonus only when it doesn't
            # collapse our separation too much.
            if (nx, ny) == (ox, oy):
                sc += 25

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]