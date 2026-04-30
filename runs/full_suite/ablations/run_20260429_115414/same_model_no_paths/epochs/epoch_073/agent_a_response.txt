def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_t = None
        best_gain = -10**9
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            gain = (od - sd) * 100 - sd
            if gain > best_gain or (gain == best_gain and (tx, ty) < best_t):
                best_gain = gain
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w // 2), (h // 2)

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        d_res_near = 0
        if resources:
            # approximate local improvement: distance to nearest resource after move
            mr = 10**9
            for rx, ry in resources:
                dd = cheb(nx, ny, rx, ry)
                if dd < mr:
                    mr = dd
            d_res_near = -mr
        else:
            d_res_near = -cheb(nx, ny, tx, ty)

        # Prefer reducing target distance; also prefer increasing opponent distance slightly.
        val = -d_self * 50 + d_opp + d_res_near
        # Deterministic tie-breakers
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]