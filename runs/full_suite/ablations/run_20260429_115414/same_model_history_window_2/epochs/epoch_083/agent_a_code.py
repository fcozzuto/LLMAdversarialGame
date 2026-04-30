def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_distance(x, y):
        if not res:
            return 0
        d = None
        for (rx, ry) in res:
            dd = cheb(x, y, rx, ry)
            if d is None or dd < d:
                d = dd
        return d if d is not None else 0

    cur_res_d = best_target_distance(sx, sy)

    res_set = set(res)
    best_mv = (0, 0)
    best_sc = -10**18

    for mv in moves:
        dx, dy = mv
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        sc = 0
        if (nx, ny) in res_set:
            sc += 1000
        nd = best_target_distance(nx, ny)
        if res:
            sc += (cur_res_d - nd) * 25

        # Deny opponent: avoid giving them immediate proximity advantage.
        opp_cur = cheb(ox, oy, sx, sy)
        opp_next = cheb(ox, oy, nx, ny)
        sc -= (opp_next - opp_cur) * 15

        if sc > best_sc:
            best_sc = sc
            best_mv = mv

    return [int(best_mv[0]), int(best_mv[1])]