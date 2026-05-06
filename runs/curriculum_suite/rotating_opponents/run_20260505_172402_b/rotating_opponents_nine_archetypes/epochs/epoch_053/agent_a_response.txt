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

    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (od - sd, -sd, tx, ty)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (0, 0) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (w - 1, h - 1)

    cur_sd = cheb(sx, sy, tx, ty)
    best_m = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nos = cheb(ox, oy, tx, ty)
        key = (nos - nsd, -nsd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_m = [dx, dy]

    if best_key is None:
        return [0, 0]

    # If we're not improving, step toward the nearest corner to reset initiative.
    if cheb(sx + best_m[0], sy + best_m[1], tx, ty) >= cur_sd:
        cx = 0 if sx <= (w - 1) / 2 else w - 1
        cy = 0 if sy <= (h - 1) / 2 else h - 1
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return best_m