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
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # pick target that maximizes advantage; tie-break toward closer to finish
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

    # one-step lookahead with obstacle avoidance
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_val = None  # (next_priority, next_my_d, next_op_d, dx, dy)

    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        next_my = cheb(nx, ny, tx, ty)
        next_op = cheb(ox, oy, tx, ty)
        # prefer moves that improve advantage; tie-break by reaching sooner
        val = (-(next_op - next_my), next_my, next_op, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move