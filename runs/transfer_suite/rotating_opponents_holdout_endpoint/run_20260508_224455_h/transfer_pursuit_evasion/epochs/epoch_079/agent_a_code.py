def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    scores = observation.get("scores") or [0, 0]
    try:
        my_score, op_score = int(scores[0]), int(scores[1])
    except Exception:
        my_score, op_score = 0, 0

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        try:
            if isinstance(r, dict):
                x, y = int(r.get("x")), int(r.get("y"))
            else:
                x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_list.append((x, y))
        except Exception:
            pass

    chase = my_score <= op_score

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        od = dist2(nx, ny, ox, oy)
        if res_list:
            rd = min(dist2(nx, ny, rx, ry) for rx, ry in res_list)
        else:
            rd = 0

        if chase:
            val = (-rd, od)  # prioritize resources, then farther from opponent
        else:
            val = (od, -rd)  # prioritize distance from opponent, then nearer to resources
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is not None:
        return best
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            return [dx, dy]
    return [0, 0]