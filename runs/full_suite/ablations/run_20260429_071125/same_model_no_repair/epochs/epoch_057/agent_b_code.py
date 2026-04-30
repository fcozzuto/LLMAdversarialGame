def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    best_res = None
    best_adv = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        key = (adv, -myd, -rx, -ry)
        if best_adv is None or key > (best_adv[0], best_adv[1]):
            best_adv = (key[0], key[1])
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    # Tie-breaker targets: if opponent is closer, try to cut them off by aiming for resources where we still have non-negative advantage;
    # otherwise, head for nearest resource directly.
    if best_adv[0] < 0:
        # find closest resource to us
        tr = min((r for r in resources if (r[0], r[1]) not in obstacles),
                 key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = tr[0], tr[1]

    # Evaluate moves: primary minimize distance to target, secondary avoid helping opponent, tertiary avoid moving into obvious chase overlap.
    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in legal:
        my_to = cheb(nx, ny, tx, ty)
        op_to = cheb(ox, oy, nx, ny)
        # Encourage approaching target; discourage moves that reduce our advantage vs opponent.
        oppd_to_target = cheb(ox, oy, tx, ty)
        my_adv_now = oppd_to_target - my_to
        score = (my_to, -my_adv_now, abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]