def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    def score_cell(rx, ry):
        d_self = abs(rx - sx) + abs(ry - sy)
        d_opp = abs(rx - ox) + abs(ry - oy)
        # Prefer cells where we are closer; still contest if opponent is closer.
        margin = d_opp - d_self
        return (margin * 100) - d_self

    if not resources:
        tx, ty = ((0, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1))
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = (abs(tx - nx) + abs(ty - ny))
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Deterministic target choice: sort then best by score_cell.
    res_sorted = sorted((tuple(r) for r in resources), key=lambda p: (p[0], p[1]))
    best_target = None
    best_target_val = None
    for rx, ry in res_sorted:
        if (rx, ry) in obstacles:
            continue
        val = score_cell(rx, ry)
        if best_target_val is None or val > best_target_val:
            best_target_val = val
            best_target = (rx, ry)
        elif val == best_target_val and best_target is not None and (rx, ry) < best_target:
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Evaluate moves by reducing race distance to target; small preference for blocking opponent.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        d_self_next = abs(tx - nx) + abs(ty - ny)
        d_opp_target = abs(tx - ox) + abs(ty - oy)
        # If we can arrive before opponent, heavily prefer.
        margin_next = d_opp_target - d_self_next
        val = (-margin_next * 120) + d_self_next
        # Nudge away from staying still if tie.
        if dx == 0 and dy == 0:
            val += 0.5
        # Deterministic tie-break by move ordering.
        cand = (val, dx, dy)
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]