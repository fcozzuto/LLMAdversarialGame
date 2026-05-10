def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            moves.append((dx, dy))
    # Deterministic preference order
    pref = {(0, 0): -0.01, (0, -1): -0.02, (0, 1): -0.03, (-1, 0): -0.04, (1, 0): -0.05,
            (-1, -1): -0.06, (1, -1): -0.07, (-1, 1): -0.08, (1, 1): -0.09}

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        best_res_val = None
        # If we can't beat opponent on any resource, still move closer to nearest resource.
        for rp in resources:
            if not (isinstance(rp, (list, tuple)) and len(rp) >= 2):
                continue
            rx, ry = int(rp[0]), int(rp[1])
            if not (0 <= rx < w and 0 <= ry < h):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Main objective: maximize our advantage (od - sd).
            # Secondary: prioritize shorter sd; tie-break by rx,ry deterministically.
            val = (od - sd, -sd, -abs(rx - nx) - abs(ry - ny), -rx, -ry)
            if best_res_val is None or val > best_res_val:
                best_res_val = val

        if best_res_val is None:
            continue

        # Small deterministic nudge to avoid ties/oscillation.
        overall = best_res_val + (pref[(dx, dy)],)
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]