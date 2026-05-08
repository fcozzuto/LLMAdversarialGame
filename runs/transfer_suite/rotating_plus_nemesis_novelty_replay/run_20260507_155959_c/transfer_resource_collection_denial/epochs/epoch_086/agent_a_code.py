def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            elif inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = None
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            d = abs(nsx - tx) + abs(nsy - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        move_best = None
        for rx, ry in resources:
            sd = md(nsx, nsy, rx, ry)
            od = md(ox, oy, rx, ry)
            # Primary: maximize opp-self distance gap (we want to be closer than opponent).
            # Secondary: minimize our distance to that resource.
            # Tertiary: break ties deterministically by preferring smaller coordinates.
            key = (od - sd, -sd, -rx - ry)
            if move_best is None or key > move_best:
                move_best = key
        if best_key is None or move_best > best_key:
            best_key = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]