def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        if 0 <= sx + 1 < w and 0 <= sy + 1 < h and (sx + 1, sy + 1) not in obstacles:
            return [1, 1]
        if 0 <= sx - 1 < w and 0 <= sy + 1 < h and (sx - 1, sy + 1) not in obstacles:
            return [-1, 1]
        return [0, 0]

    best_res = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach at least as fast, and if so, where we are more ahead.
        key = (od - sd, -sd, -(abs(tx - sx) + abs(ty - sy)), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    best_move = None
    best_mv_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Move step: reduce distance to target, but keep deterministic tie-breaking.
        d_after = cheb(nx, ny, tx, ty)
        d_before = cheb(sx, sy, tx, ty)
        # Slightly discourage stepping away from target.
        key = (d_before - d_after, -d_after, -(abs(nx - tx) + abs(ny - ty)), dx, dy)
        if best_mv_key is None or key > best_mv_key:
            best_mv_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]