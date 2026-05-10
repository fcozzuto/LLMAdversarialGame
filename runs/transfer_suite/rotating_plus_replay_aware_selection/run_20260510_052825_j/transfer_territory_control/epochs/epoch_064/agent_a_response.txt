def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    unclaimed = observation.get("unclaimed_cells") or []
    oppT = observation.get("opponent_territory") or []
    selfT = observation.get("self_territory") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in selfT)
    oppT = set(tuple(p) for p in oppT)
    unclaimed_set = set(tuple(p) for p in unclaimed)

    if not unclaimed and not oppT:
        return [0, 0]

    # Pick a deterministic target: nearest unclaimed, else nearest opponent territory
    # Tie-break by y then x for determinism.
    def best_target(cells):
        tx, ty = None, None
        best = (10**9, 10**9, 10**9)
        for cx, cy in cells:
            d = abs(cx - x) + abs(cy - y)
            t = (d, cy, cx)
            if t < best:
                best = t
                tx, ty = cx, cy
        return tx, ty

    if unclaimed:
        tx, ty = best_target(unclaimed)
    else:
        tx, ty = best_target(oppT)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best_move = (0, 0)
    best_val = -10**18

    # Small deterministic bias to reduce obstacle hits: prefer diagonal/straight order as listed
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: decrease distance to target
        dist_now = abs(x - tx) + abs(y - ty)
        dist_next = abs(nx - tx) + abs(ny - ty)
        val = (dist_now - dist_next) * 10.0

        # Territory control preference
        if (nx, ny) in unclaimed_set:
            val += 70.0
        elif (nx, ny) in oppT:
            val += 35.0
        elif (nx, ny) in selfT:
            val += 8.0
        else:
            val += 1.0

        # Frontier/escape pressure: slightly prefer moves that have at least one reachable unclaimed nearby
        near_unclaimed = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                mx, my = nx + ax, ny + ay
                if inb(mx, my) and (mx, my) in unclaimed_set:
                    near_unclaimed += 1
        val += near_unclaimed * 2.5

        # Mild anti-stuck: if moving to a cell with fewer legal exits, penalize
        exits = 0
        for ex, ey in deltas:
            xx, yy = nx + ex, ny + ey
            if inb(xx, yy) and (xx, yy) not in obstacles:
                exits += 1
        val -= (9 - exits) * 0.3

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]