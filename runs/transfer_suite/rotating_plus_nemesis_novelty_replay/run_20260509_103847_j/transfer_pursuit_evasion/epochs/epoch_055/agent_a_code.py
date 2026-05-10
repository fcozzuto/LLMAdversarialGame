def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def in_bounds_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_evader = "evader" in sr or ("evade" in sr) or ("escape" in sr)
    opp_pursuer = ("purs" in pr) or ("chaser" in pr) or ("catch" in pr) or ("hunt" in pr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = moves[4]
    best_val = None

    # Evaluate next position for either pursuer (minimize) or evader (maximize)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds_free(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        man = abs(ddx) + abs(ddy)

        # Small tie-break: prefer moves that create/avoid diagonal alignment with opponent
        diag_align = (1 if (ddx == 0 or ddy == 0) else 0)  # penalize staying aligned on axis
        to_opp = (abs(ox - nx) + abs(oy - ny))

        # Boundary safety
        edge_pen = 0
        if nx == 0 or nx == w - 1:
            edge_pen += 0.25
        if ny == 0 or ny == h - 1:
            edge_pen += 0.25

        if self_evader or (opp_pursuer and not ("purs" in sr or "chaser" in sr or "catch" in sr or "hunt" in sr)):
            # Evader: maximize distance; also bias away in direction of opponent.
            val = d2 + 0.15 * man - 0.1 * edge_pen - 0.05 * diag_align - 0.01 * to_opp
            better = (best_val is None) or (val > best_val)
        else:
            # Pursuer: minimize distance; prefer reducing both components (cut off wall-run style).
            comp = (abs(ddx) + abs(ddy))
            val = -d2 - 0.2 * comp + 0.05 * to_opp - 0.1 * edge_pen - 0.02 * diag_align
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]