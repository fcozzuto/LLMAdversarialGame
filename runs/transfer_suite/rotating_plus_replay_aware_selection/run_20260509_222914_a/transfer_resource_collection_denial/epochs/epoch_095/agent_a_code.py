def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    # Distance in turns with diagonal moves allowed (Chebyshev)
    def d(a, b, c, e):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - e
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Evaluate this move by best contested resource (prefer we arrive earlier)
        move_best = None
        for rx, ry in resources:
            ts = d(nx, ny, rx, ry)
            to = d(ox, oy, rx, ry)
            # Primary: advantage in time (earlier => larger), Secondary: prefer closer if tie
            advantage = to - ts
            val = (advantage, -ts)
            if move_best is None or val > move_best:
                move_best = val
        if best is None or move_best > best:
            best = move_best
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]