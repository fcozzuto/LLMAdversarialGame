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
    moves.sort(key=lambda d: (d[0], d[1]))

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        border_f = min(nx, ny, (w - 1 - nx), (h - 1 - ny))  # bigger => farther from edges

        # Obstacle proximity penalty/bonus (deterministic local check)
        obs_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    obs_near += 1

        # Evader wants large separation and avoid corners; pursuer wants small separation and avoid edges if ties
        if is_evader:
            val = (dist * 100) + (border_f * 5) - (obs_near * 3)
        else:
            val = (-dist * 100) + (border_f * 1) - (obs_near * 3)

        if best_val is None or (val > best_val if is_evader else val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move