def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    center_bias = 1.0 if observation.get("turn_index", 0) < 20 else 0.4

    # Pick a primary target among unclaimed: prioritize closeness to us, but slightly favor far-from-opponent.
    target = None
    if unclaimed:
        best = (10**9, 10**9, 10**9)
        for cx, cy in unclaimed:
            if (cx, cy) in obstacles:
                continue
            d_us = abs(cx - sx) + abs(cy - sy)
            d_opp = abs(cx - ox) + abs(cy - oy)
            # lower is better for tuple
            cand = (d_us, -d_opp, cx + cy * 0.0001)
            if cand < best:
                best = cand
                target = (cx, cy)
    if target is None:
        target = (int(center[0]), int(center[1]))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Immediate capture value
        if cell in opp_cells:
            base = 1000000
        elif cell in unclaimed:
            base = 2000
        elif cell in self_cells:
            base = 200
        else:
            base = 500  # (rare) if cell not categorized

        # Tactical pressure: race opponent and head towards target/center
        d_to_target = abs(nx - target[0]) + abs(ny - target[1])
        d_opp_now = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - center[0]) + abs(ny - center[1])

        score = base
        score -= 10 * d_to_target
        score += 2 * d_opp_now  # keep distance from opponent to avoid being flipped back (deterministic risk control)
        score -= center_bias * 1.5 * d_center

        # Tie-break deterministically by lexicographic move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]