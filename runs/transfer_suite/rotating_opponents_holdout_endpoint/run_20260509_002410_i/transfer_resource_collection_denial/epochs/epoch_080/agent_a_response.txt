def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None  # (priority, my_d, op_d, tx, ty)
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
        lead = my_d - op_d  # <=0 means we are earlier or tie
        # Prioritize: can reach no later than opponent, then smaller my distance, then smaller opponent distance.
        priority = 0 if lead <= 0 else 1
        cand = (priority, my_d, op_d, tx, ty)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]

    tx = int(best[3]); ty = int(best[4])
    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx = sx + dx
    ny = sy + dy
    if (nx, ny) in obstacles:
        # Try alternate axis step deterministically.
        if dx != 0:
            alt = (0, dy)
            nx2, ny2 = sx + alt[0], sy + alt[1]
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [alt[0], alt[1]]
        if dy != 0:
            alt = (dx, 0)
            nx2, ny2 = sx + alt[0], sy + alt[1]
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [alt[0], alt[1]]
        return [0, 0]

    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]