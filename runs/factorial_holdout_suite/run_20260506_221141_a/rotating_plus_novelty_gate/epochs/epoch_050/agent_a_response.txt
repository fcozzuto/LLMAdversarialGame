def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                if (x, y) not in res_set:
                    res_set.add((x, y))
                    resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in res_set:
        return [0, 0]

    def kdist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    safe_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            safe_moves.append((dx, dy, nx, ny))
        else:
            if (sx, sy) not in blocked:
                safe_moves.append((0, 0, sx, sy))

    # Choose move that maximizes guaranteed-first chances for the best contested resource.
    best_score = None
    best = (0, 0)
    for dx, dy, nx, ny in safe_moves:
        local_best = None
        for rx, ry in resources:
            my = kdist(nx, ny, rx, ry)
            opp = kdist(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; then closeness.
            # Penalize giving opponent a closer claim.
            claim = 0
            if my <= opp:
                claim += 1000
                claim += (opp - my) * 3
            claim -= my
            claim -= (my - opp) if my > opp else 0
            # Slight preference to resources closer to center to reduce corner-trap.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            claim -= 0.01 * (abs(rx - cx) + abs(ry - cy))
            if local_best is None or claim > local_best:
                local_best = claim
        if best_score is None or local_best > best_score:
            best_score = local_best
            best = (dx, dy)
        elif local_best == best_score:
            # Deterministic tie-break: lowest dx, then lowest dy, then prefer moving.
            bx, by = best
            if (dx, dy) < (bx, by):
                best = (dx, dy)
    return [int(best[0]), int(best[1])]