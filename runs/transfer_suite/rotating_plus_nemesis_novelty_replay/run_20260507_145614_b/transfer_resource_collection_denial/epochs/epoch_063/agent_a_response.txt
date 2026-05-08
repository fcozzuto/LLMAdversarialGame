def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any((sx, sy) == (r[0], r[1]) for r in resources):
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi, dyi = 0, 0

        opp_after = dist(nx, ny, ox, oy)
        cur_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            myd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - myd  # positive = likely to deny/reach first
            val = adv * 1000 - myd * 3 - opp_after
            if myd == 0:
                val += 10**9
            if val > cur_best:
                cur_best = val
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dxi, dyi)

    return [int(best_move[0]), int(best_move[1])]