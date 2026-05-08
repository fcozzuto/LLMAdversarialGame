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
    # Fixed deterministic move ordering for tie-breaks
    moves.sort(key=lambda d: (d[0], d[1]))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        d = max(abs(nx - ox), abs(ny - oy))  # pursuer/evader works with Chebyshev
        # Additional heuristic: avoid moving to being "cornered" too early when evading
        corner_score = 0
        if is_evader:
            corner_score = min(nx, ny, w - 1 - nx, h - 1 - ny)  # larger => farther from border
        # Enemy escape pressure: prefer increasing distance overall; break ties by border distance
        if is_evader:
            key = (-d, -corner_score, dx, dy)
        else:
            key = (d, -min(nx, ny, w - 1 - nx, h - 1 - ny), dx, dy)

        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]