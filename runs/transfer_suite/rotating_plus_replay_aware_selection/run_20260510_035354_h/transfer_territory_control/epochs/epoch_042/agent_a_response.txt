def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if inb(p[0], p[1]))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    targets = [p for p in unclaimed if inb(p[0], p[1])]
    if not targets:
        targets = [p for p in unclaimed if inb(p[0], p[1])]  # keep deterministic no-op
    if not targets:
        targets = [p for p in opp_terr if inb(p[0], p[1])]

    # If still none (rare), move toward center while avoiding obstacles.
    if not targets:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestd = 10**18
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return [int(best[0]), int(best[1])]

    # Limit consideration for speed.
    candidates = targets
    if len(candidates) > 24:
        candidates = sorted(candidates, key=lambda p: (abs(p[0] - ax) + abs(p[1] - ay), p[0], p[1]))[:24]

    # Score each move by best achievable target preference.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer stepping into new territory/unclaimed; secondarily avoid giving opponent easy control.
        step_bonus = 0
        if (nx, ny) in unclaimed:
            step_bonus += 6
        if (nx, ny) in opp_terr:
            step_bonus += 3  # flipping is allowed; generally good
        if (nx, ny) in self_terr:
            step_bonus += 1

        # Evaluate distance to best target (lower is better), and distance from opponent (higher is better).
        best_t = 10**18
        best_foe = -10**18
        for tx, ty in candidates:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_t:
                best_t = d
                best_foe = abs(tx - ox) + abs(ty - oy)
            elif d == best_t:
                best_foe = max(best_foe, abs(tx - ox) + abs(ty - oy))

        # Nearer target, farther from opponent. Deterministic tie-break by move order.
        score = step_bonus * 100 - best_t * 10 + best_foe
        if score > best_score:
            best_score, best_move = score, (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]