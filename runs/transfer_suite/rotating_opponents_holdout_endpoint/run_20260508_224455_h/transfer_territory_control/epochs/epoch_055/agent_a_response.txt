def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for c in obstacles:
        if c is not None and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    own = set((int(x), int(y)) for x, y in self_t if x is not None and y is not None)
    opp = set((int(x), int(y)) for x, y in opp_t if x is not None and y is not None)
    uq = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Build frontier targets: unclaimed cells adjacent to opponent territory; prefer those.
    frontier = []
    if opp:
        for (x, y) in uq:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp:
                    frontier.append((x, y))
                    break

    # Fallback: any unclaimed
    targets = frontier if frontier else list(uq)
    if not targets:
        return [0, 0]

    # Deterministic target choice: closest to us, tie-break by coordinates
    cx, cy = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Heuristic value: prefer stealing/claiming, then moving toward frontier.
        if (nx, ny) in opp:
            val = 5.0
        elif (nx, ny) in uq:
            val = 3.0
        elif (nx, ny) in own:
            val = 1.0
        else:
            val = 1.0  # should be rare

        # Encourage moving closer to target; penalize leaving it behind.
        dist_now = abs(nx - cx) + abs(ny - cy)
        dist_cur = abs(sx - cx) + abs(sy - cy)
        val += 0.2 * (dist_cur - dist_now)

        # Slightly prefer non-stagnation toward a target when possible.
        if (dx, dy) == (0, 0) and dist_now > 0:
            val -= 0.4

        # Deterministic tie-break: smaller dx, then dy.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]