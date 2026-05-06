def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    def best_resource_for(nx, ny):
        if not resources:
            return None, None
        best = None
        best_r = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer large "denial" gap, then closer resources.
            val = (do - ds, -ds, -(abs(rx - ox) + abs(ry - oy)), rx, ry)
            if best is None or val > best:
                best = val
                best_r = (rx, ry)
        return best, best_r

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us in place
        res_val, _ = best_resource_for(nx, ny)
        if res_val is None:
            # No usable resources: go to deny by approaching opponent.
            s_to_o = cheb(nx, ny, ox, oy)
            score = (-s_to_o, 0, 0, nx, ny)
        else:
            # res_val already encodes (do-ds, -ds, ...)
            s_to_o = cheb(nx, ny, ox, oy)
            score = (res_val[0], res_val[1], res_val[2], -s_to_o, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move