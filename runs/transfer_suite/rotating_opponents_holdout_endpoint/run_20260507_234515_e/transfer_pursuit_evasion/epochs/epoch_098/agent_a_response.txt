def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        border_f = min(nx, ny, (w - 1 - nx), (h - 1 - ny))  # higher = safer from edges

        obs_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in blocked:
                    obs_near += 1

        # Small bias to reduce oscillations: prefer continuing direction when not blocked
        cont = 0
        if 0 <= sx + dx < w and 0 <= sy + dy < h and (sx + dx, sy + dy) not in blocked:
            cont = 1

        if is_evader:
            val = (dist * 10.0) + (border_f * 1.2) + (cont * 0.15) - (obs_near * 1.0)
        else:
            val = (-dist * 10.0) + (border_f * 0.2) + (cont * 0.1) - (obs_near * 1.0)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]