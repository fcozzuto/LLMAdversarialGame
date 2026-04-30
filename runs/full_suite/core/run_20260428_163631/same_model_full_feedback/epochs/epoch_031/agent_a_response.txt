def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sp[0]), int(sp[1]), int(op[0]), int(op[1])

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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = None
        best_v = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            v = (sd - 0.9 * od)  # prioritize resources we contest/reach first
            if best_v is None or v < best_v or (v == best_v and (tx < best_t[0] or (tx == best_t[0] and ty < best_t[1]))):
                best_v = v
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    cur_res = cheb(sx, sy, tx, ty)
    cur_opp = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nr = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # prefer faster convergence; also maintain separation to avoid being "raced" into same area
        sc = (cur_res - nr) * 10 + (no - cur_opp) * 0.5 - nr * 0.2 + (1.0 if (dx, dy) == (0, 0) else 0.0) * 0.0
        if best is None or sc > best or (sc == best and (dx, dy) < best_move):
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]