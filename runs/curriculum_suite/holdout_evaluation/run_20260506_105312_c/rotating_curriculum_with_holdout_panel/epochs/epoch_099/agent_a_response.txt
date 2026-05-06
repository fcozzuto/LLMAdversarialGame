def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            v = d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    if not inb(sx, sy) or (sx, sy) in obs:
        sx, sy = 0, 0

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Deterministic tie-break: prefer fewer dx^2+dy^2, then lexicographic.
    def step_pref(dx, dy):
        return (dx * dx + dy * dy, dx, dy)

    opp_has_bonus = []
    # Precompute opponent distances to each resource for contest awareness.
    for rx, ry in resources:
        opp_has_bonus.append(abs(rx - ox) + abs(ry - oy))

    best_move = [0, 0]
    best_val = -10**18
    tie = (10**9, 10**9, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose the single best resource according to "grab if not heavily contested".
        best_res_val = -10**18
        for i, (rx, ry) in enumerate(resources):
            d_self = abs(rx - nx) + abs(ry - ny)
            d_opp = opp_has_bonus[i]

            # If opponent is closer, this resource is less attractive; but if we can still reach very fast, allow.
            contested = d_opp - d_self
            # Prefer resources that we can reasonably beat, and also avoid running into opponent.
            reach_fast = 6 - d_self
            avoid_opp = abs(nx - ox) + abs(ny - oy)

            v = (10 * reach_fast) + (2 * contested) + (0.15 * avoid_opp)
            if v > best_res_val:
                best_res_val = v

        # Small preference to keep movement stable (helps when opponent sweeps).
        total = best_res_val - 0.01 * (dx * dx + dy * dy)
        t = (step_pref(dx, dy)[0], step_pref(dx, dy)[1], step_pref(dx, dy)[2])

        if total > best_val or (total == best_val and t < tie):
            best_val = total
            tie = t
            best_move = [int(dx), int(dy)]

    return best_move