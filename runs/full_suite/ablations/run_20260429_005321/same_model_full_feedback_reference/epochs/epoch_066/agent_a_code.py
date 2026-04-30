def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_to(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    target = None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = score_to(sx, sy, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
                target = (rx, ry)
    else:
        target = (w - 1, h - 1) if (sx <= w // 2 and sy <= h // 2) else (0, 0)

    if valid(ox, oy):
        pass

    # Try to take a resource cell if already on target; otherwise move toward it.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer stepping onto resources
        if (nx, ny) in resources:
            val = 10**12
        else:
            val = -score_to(nx, ny, target[0], target[1])
            # If close to opponent, slightly prefer moving away
            if score_to(nx, ny, ox, oy) <= 4:
                val += score_to(nx, ny, ox, oy) * 2
            # If resources are empty, bias toward corner target
            if not resources:
                val += score_to(nx, ny, target[0], target[1]) * -0.1
        # Deterministic tie-break: smallest dx, then dy
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]