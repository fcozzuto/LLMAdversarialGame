def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - our_d
        key = (-adv, our_d, rx, ry)  # want max adv, then min our_d
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    our_on_resource = (sx, sy) == (tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_d2 = cheb(nx, ny, tx, ty)
        opp_d2 = cheb(ox, oy, tx, ty)
        adv2 = opp_d2 - our_d2

        on_res = (nx, ny) == (tx, ty)
        closer = our_d2 < cheb(sx, sy, tx, ty)
        tie_bonus = 1 if adv2 > (opp_d2 - cheb(sx, sy, tx, ty)) else 0

        val = (
            -adv2,              # maximize advantage
            our_d2,             # then minimize our distance
            0 if on_res else 1, # prefer stepping onto target
            0 if closer else 1,  # prefer progress
            dx, dy
        )
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if not our_on_resource and best_move == (0, 0):
        # If stuck, deterministically move toward target
        stepx = 0 if tx == sx else (1 if tx > sx else -1)
        stepy = 0 if ty == sy else (1 if ty > sy else -1)
        for cand in [(-stepx, -stepy), (stepx, stepy), (stepx, 0), (0, stepy), (0, 0)]:
            cx, cy = sx + cand[0], sy + cand[1]
            if inb(cx, cy):
                return [cand[0], cand[1]]
    return [best_move[0], best_move[1]]