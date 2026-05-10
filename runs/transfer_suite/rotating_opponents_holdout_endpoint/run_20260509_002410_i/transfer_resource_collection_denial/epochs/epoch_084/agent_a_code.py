def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
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

    best_t = None
    best_key = None  # smaller is better
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
        # Prefer where we are much closer than opponent; tie -> closer to it.
        key = (-(op_d - my_d), my_d, op_d, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x2 = sx + dx
            y2 = sy + dy
            if 0 <= x2 < w and 0 <= y2 < h and (x2, y2) not in obstacles:
                deltas.append((dx, dy))

    if not deltas:
        return [0, 0]

    best_move = None
    best_move_key = None  # smaller is better
    for dx, dy in deltas:
        x2 = sx + dx
        y2 = sy + dy
        my_d2 = cheb(x2, y2, tx, ty)
        op_d2 = cheb(ox, oy, tx, ty)
        # Also slightly penalize increasing distance to target.
        key = (-((op_d2 - my_d2)), my_d2, abs(dx) + abs(dy), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]