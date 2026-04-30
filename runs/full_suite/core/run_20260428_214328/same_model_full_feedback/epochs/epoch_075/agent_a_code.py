def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if resources:
            best = None
            best_key = None
            for rx, ry in resources:
                myd = md(sx, sy, rx, ry)
                opd = md(ox, oy, rx, ry)
                adv = opd - myd
                key = (adv, -myd, rx, ry)
                if best_key is None or key > best_key:
                    best_key = key
                    best = (rx, ry)
            return best
        cx, cy = w // 2, h // 2
        if ok(cx, cy):
            return (cx, cy)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = cx + dx, cy + dy
                if ok(nx, ny):
                    return (nx, ny)
        return (sx, sy)

    tx, ty = best_target()

    # Choose a step that reduces distance to target, with deterministic tie-breaks
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        # Secondary pressure: don't walk into allowing opponent closer advantage to the same target
        opp_d = md(ox, oy, tx, ty)
        score = (-(d), (opp_d - d), -abs((nx - tx)) - abs((ny - ty)), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        # If something odd happened (shouldn't), stay still deterministically
        return [0, 0]
    return [int(dx), int(dy)]