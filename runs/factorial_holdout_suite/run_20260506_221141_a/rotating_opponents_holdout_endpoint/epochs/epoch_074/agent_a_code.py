def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        d_ours = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Lower is better: we prefer being much closer than opponent.
        # If close-call, prioritize targets where opponent is farther.
        key = (d_ours - 0.85 * d_opp, d_opp, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()
    cur_d = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        # Prefer reducing our distance to target, then increase separation from opponent,
        # then prefer moves that improve over staying.
        val = (d1 - cur_d, -d2, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move