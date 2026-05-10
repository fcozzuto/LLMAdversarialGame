def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    scores = observation.get("scores")
    my_score = 0
    op_score = 0
    if isinstance(scores, dict):
        for k in ("self", "me", "player", "agent"):
            if k in scores:
                my_score = scores[k]
        for k in ("opponent", "opp", "enemy", "enemy_agent"):
            if k in scores:
                op_score = scores[k]
        if my_score == 0 and "self" not in scores and "me" not in scores:
            for k, v in scores.items():
                if v == scores.get("self_score", None):
                    my_score = v
                elif v == scores.get("opponent_score", None):
                    op_score = v
    elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
        my_score = scores[0]
        op_score = scores[1]

    chase = my_score < op_score

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        val = -d if chase else d
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is not None:
        return best
    return [0, 0]