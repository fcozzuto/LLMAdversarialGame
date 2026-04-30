def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_target(rx, ry):
        ourd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        # Prefer targets we're closer to; if opponent closer, penalize harder.
        adv = oppd - ourd
        return adv * 1000 - ourd * 3 + (rx + 7 * ry)

    if resources:
        # Choose a strong target deterministically
        best_t = None
        best_k = None
        for rx, ry in resources:
            k = (score_target(rx, ry), -(rx * 31 + ry))
            if best_k is None or k > best_k:
                best_k = k
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # If target is known, move to improve our distance vs opponent to that target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ourd2 = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        # Aim to beat opponent on the target, also keep away from obstacles by discouraging staying adjacent? (cheap)
        val = (oppd - ourd2) * 1000 - ourd2 * 3 - (dx == 0 and dy == 0) * 2
        # Mildly prefer moves that also reduce distance to any nearby resource (obstacle-agnostic)
        for rx, ry in resources[:min(6, len(resources))]:
            if man(nx, ny, rx, ry) <= man(nx, ny, tx, ty) + 2:
                val += 5 - man(nx, ny, rx, ry)
        # Tie-break: prefer direction that doesn't drift toward opponent corner
        val += -(man(nx, ny, ox, oy) // 2)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]