def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = max(abs(nx - tx), abs(ny - ty))
            cand = (d, abs(ox - nx) - abs(ox - sx), abs(dx) + abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    res_set = {(r[0], r[1]) for r in resources}
    best = None
    best_move = (0, 0)

    # Deterministic preference: maximize (opponent advantage over us) reduction.
    # If a move lands on a resource, strongly prioritize it.
    for dx, dy, nx, ny in valid:
        on_resource = 1 if (nx, ny) in res_set else 0
        if on_resource:
            # Try to take immediately; tie-break by minimizing opponent distance to that same cell.
            opp_d = abs(nx - ox) + abs(ny - oy)
            cand = (-999999, opp_d, abs(nx - sx) + abs(ny - sy), dx, dy)
        else:
            best_adv = -10**9
            best_sd = 10**9
            # Evaluate best resource for us after this move, penalize resources where opponent is closer.
            for rx, ry in res_set:
                sd = abs(nx - rx) + abs(ny - ry)
                od = abs(ox - rx) + abs(oy - ry)
                adv = od - sd  # larger means we are closer than opponent (more favorable)
                if adv > best_adv or (adv == best_adv and sd < best_sd):
                    best_adv = adv
                    best_sd = sd
            # Convert to minimization tuple for deterministic selection
            # Prefer higher best_adv, then smaller distance to that target, then keep away from obstacles by lower move cost.
            cand = (-best_adv, best_sd, dx * dx + dy * dy, dx, dy)
        if best is None or cand < best:
            best = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]