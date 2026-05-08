def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    best = None
    best_key = None
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi, dyi = 0, 0

        # Choose the resource that gives the most advantage with this step.
        move_best_adv = -10**9
        move_best_sd = 10**9
        move_best_od = 10**9
        for rx, ry in resources:
            sd = cd(sx, sy, rx, ry)
            nd = cd(nx, ny, rx, ry)
            od = cd(ox, oy, rx, ry)
            adv = (od - nd)
            if adv > move_best_adv or (adv == move_best_adv and (nd < move_best_sd or (nd == move_best_sd and od < move_best_od))):
                move_best_adv, move_best_sd, move_best_od = adv, nd, od

        # Prefer larger advantage; then closer self; then keep away from opponent if still tied.
        key = (move_best_adv, -move_best_sd, -(move_best_od))
        if best_key is None or key > best_key:
            best_key = key
            best = [dxi, dyi]

    return best