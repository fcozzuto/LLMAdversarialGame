def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    # If no resources, drift toward center to reduce tie losses
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose our nearest resource; also compute opponent pressure as secondary term
    best_res = None
    best_my_dist = 10**9
    for (rx, ry) in resources:
        d = manh(sx, sy, rx, ry)
        if d < best_my_dist:
            best_my_dist = d
            best_res = (rx, ry)

    # If opponent is closer to that resource, pick our next best that is not too contested
    if best_res is not None:
        rx, ry = best_res
        opp_d = manh(ox, oy, rx, ry)
        if opp_d + 1 < best_my_dist:
            best_my_dist = 10**9
            cand = None
            for (rx, ry) in resources:
                d = manh(sx, sy, rx, ry)
                od = manh(ox, oy, rx, ry)
                # Prefer resources where we are at least as close as opponent
                score = (0 if d <= od else 1) * 1000 + d - od
                # deterministic tie-break
                if score < best_my_dist:
                    best_my_dist = score
                    cand = (rx, ry)
            if cand is not None:
                best_res = cand

    rx, ry = best_res
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0, 10**18)

    # Score each legal step by how much it reduces distance to target,
    # plus a small deterministic term to avoid oscillation and to account for opponent pressure.
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = manh(nx, ny, rx, ry)
        opp_d = manh(nx, ny, ox, oy)
        # Opponent pressure: if we step into squares closer to opponent, slightly penalize.
        # Also incorporate parity-based tie-break deterministically.
        det = ((nx + 3 * ny + ti) % 7) * 0.001
        score = my_d * 10.0 + opp_d * 0.05 + det
        if score < best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]