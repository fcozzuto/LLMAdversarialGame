def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tcx, tcy = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = (10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d_op = abs(nx - ox) + abs(ny - oy)
            d_corner = abs(nx - tcx) + abs(ny - tcy)
            # Strongly prioritize closing on opponent, then herding to her nearest corner.
            score = d_op * 1000 + d_corner
            # Deterministic tie-break: prefer moves that reduce dx/dy magnitude, then lexicographic.
            score2 = (score, abs(dx) + abs(dy), dx, dy)
            if score2 < best:
                best = score2
    _, _, dx, dy = best
    return [int(dx), int(dy)]