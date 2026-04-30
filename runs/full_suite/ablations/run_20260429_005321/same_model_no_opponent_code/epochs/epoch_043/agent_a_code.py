def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # Target selection: maximize how much closer we are than opponent (deterministic).
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds
        key = (margin, -ds, -((rx + ry) % 7), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Move: among legal deltas, choose one that reduces our cheb distance to target,
    # while also discouraging getting closer to opponent (helps contest).
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cur_ds = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside_free(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndop = cheb(nx, ny, ox, oy)
        # Primary: reduce our distance to target; Secondary: increase opponent distance;
        # Tertiary: slight preference for progressing toward target axes.
        progress = abs(tx - nx) + abs(ty - ny)
        score = (-(nds - cur_ds), -ndop, -progress, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if not best_score:
        return [0, 0]
    return best_move