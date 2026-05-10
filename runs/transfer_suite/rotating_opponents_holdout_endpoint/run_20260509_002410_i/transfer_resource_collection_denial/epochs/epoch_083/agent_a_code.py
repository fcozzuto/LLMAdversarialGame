def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick target: maximize (my advantage) = op_dist - my_dist ; tie -> closer by my_dist
    best = None  # (-(adv), my_d, op_d, tx, ty)
    for r in resources:
        if not r or len(r) < 2:
            continue
        tx = int(r[0]); ty = int(r[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue
        my_d = cheb(sx, sy, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        adv = op_d - my_d
        cand = (-adv, my_d, op_d, tx, ty)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    _, _, _, tx, ty = best

    def step_moves():
        ms = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        # deterministic ordering already
        return ms

    # evaluate candidate steps by resulting dist advantage; avoid obstacle squares
    cur_my_d = cheb(sx, sy, tx, ty)
    cur_op_d = cheb(ox, oy, tx, ty)
    bestm = None  # (score, tie) lower better
    for dx, dy in step_moves():
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, tx, ty)
        # prefer improving toward target, and preventing opponent from getting closer advantage
        adv = cur_op_d - my_d
        # primary: maximize adv -> minimize -adv; secondary: minimize my_d; tertiary: minimize distance to any resource if tied
        score = (-adv, my_d)
        if bestm is None or score < bestm:
            bestm = score
            best_move = [dx, dy]

    if bestm is None:
        return [0, 0]
    return best_move