def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((mx, my, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        # Fall back: move toward center while keeping distance from opponent.
        cx, cy = (w - 1) / 2, (h - 1) / 2
        best = None
        bestv = None
        for mx, my, nx, ny in valid:
            v = (abs(nx - cx) + abs(ny - cy), -(abs(nx - ox) + abs(ny - oy)))
            if bestv is None or v < bestv:
                bestv = v
                best = (mx, my)
        return list(best if best is not None else (0, 0))

    # Deterministic evaluation: chase a best "swing" resource; if opponent is closer, still
    # prioritize moves that reduce their edge (resource_denier mitigation).
    best_move = (0, 0)
    best_score = None
    for mx, my, nx, ny in valid:
        my_pos = nx, ny
        # Prefer avoiding stepping into immediate opponent reach when resources are scarce.
        deny_adj = abs(nx - ox) + abs(ny - oy)
        base = -0.02 * deny_adj

        best_res = None
        best_res_score = None
        for rx, ry in resources:
            se = abs(nx - rx) + abs(ny - ry)
            oe = abs(ox - rx) + abs(oy - ry)
            # Lead on resource: positive when we are closer than opponent.
            lead = (oe - se)
            # Penalize long travel, encourage short/contested wins.
            s = lead * 2.0 - se * 0.35 + (1.2 if (se == 0) else 0.0)
            if best_res_score is None or s > best_res_score:
                best_res_score = s
                best_res = (rx, ry, se, oe)
        # Secondary tie-break: closer to chosen resource target; also discourage giving opponent closer access.
        rx, ry, se, oe = best_res
        score = base + best_res_score - 0.05 * se + 0.02 * (oe - se)
        if best_score is None or score > best_score or (score == best_score and (se, -oe) < (abs(sx - rx) + abs(sy - ry), 0)):
            best_score = score
            best_move = (mx, my)

    return [best_move[0], best_move[1]]