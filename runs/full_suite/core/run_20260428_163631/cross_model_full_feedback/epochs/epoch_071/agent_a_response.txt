def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Precompute resource ordering for determinism
    res_sorted = sorted(resources)

    # Evaluate each move by competitive advantage over a few nearest resources.
    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        us_pos = (nx, ny)
        # Score: prioritize resources where we're closer than opponent, otherwise still prefer proximity.
        scored = []
        for rx, ry in res_sorted[:12]:
            rpos = (rx, ry)
            d_us = dist(us_pos, rpos)
            d_opp = dist((ox, oy), rpos)
            # Advantage: positive when we are closer than opponent.
            adv = d_opp - d_us
            # Penalties to avoid stalling and moving away from any resource.
            proximity = -d_us
            # Weight closer competitive wins more.
            val = 3.0 * adv + 1.2 * proximity
            scored.append(val)
        if scored:
            # Use top-k to focus on likely grabs.
            scored.sort(reverse=True)
            s = scored[0] + (scored[1] * 0.6 if len(scored) > 1 else 0) + (scored[2] * 0.35 if len(scored) > 2 else 0)
        else:
            s = 0.0

        # Tie-break: prefer reducing distance to the single best resource for us after move.
        if resources:
            target = min(resources, key=lambda r: (dist(us_pos, r), r[0], r[1]))
            tie_d = dist(us_pos, target)
        else:
            tie_d = abs(nx - (w // 2)) + abs(ny - (h // 2))
        key = (s, -tie_d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]