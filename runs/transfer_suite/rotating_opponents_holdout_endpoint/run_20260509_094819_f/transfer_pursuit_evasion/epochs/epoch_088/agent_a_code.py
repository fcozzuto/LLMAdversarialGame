def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res_list = observation.get("resources") or []
    have_res = bool(res_list) and (observation.get("remaining_resource_count", 1) or 0) != 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def nearest_res_dist(x, y):
        best = 10**9
        for r in res_list:
            if r and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if 0 <= rx < w and 0 <= ry < h:
                    d = cheb(x, y, rx, ry)
                    if d < best:
                        best = d
        return best if best != 10**9 else 0

    best_move = moves[0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d_op = cheb(nx, ny, ox, oy)
        if have_res:
            d_rs = nearest_res_dist(nx, ny)
            val = 3.0 * d_op - 1.0 * d_rs
        else:
            val = d_op
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]