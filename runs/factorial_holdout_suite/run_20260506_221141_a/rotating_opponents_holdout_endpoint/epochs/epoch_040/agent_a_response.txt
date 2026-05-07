def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # If opponent can reach sooner, devalue heavily; otherwise favor closer and "upper" progress.
        lead = d_op - d_me
        progress = (ry * 2 + rx)
        key = (0,)
        if lead < 0:
            key = (1, d_me, d_op, -progress)  # worse: likely stolen/denied
        else:
            key = (0, d_me, -lead, -progress)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cur_dist = cheb(sx, sy, tx, ty)
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Choose step that reduces distance most; tie-break by moving toward tx/ty and away from opponent.
        opp_d = cheb(nx, ny, ox, oy)
        step_key = (-(cur_dist - d), d, -opp_d, (0 if dx == 0 else (1 if dx > 0 else 0)), (0 if dy == 0 else (1 if dy > 0 else 0)))
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]