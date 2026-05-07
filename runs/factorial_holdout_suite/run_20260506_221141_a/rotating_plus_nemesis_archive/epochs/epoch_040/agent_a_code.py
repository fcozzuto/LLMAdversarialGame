def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        return [0, 0]
    if not (0 <= sx < w and 0 <= sy < h and 0 <= ox < w and 0 <= oy < h):
        return [0, 0]

    obstacles_raw = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**9

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                my_d = 10**9
                opp_d = 10**9
                for rx, ry in resources:
                    dmy = cheb(nx, ny, rx, ry)
                    dop = cheb(ox, oy, rx, ry)
                    if dmy < my_d:
                        my_d = dmy
                        opp_d = dop
                val = (opp_d - my_d) * 1000 - my_d
                if val > best_val or (val == best_val and (dx, dy) < best):
                    best_val = val
                    best = (dx, dy)
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                dist = cheb(nx, ny, ox, oy)
                if dist > best_val or (dist == best_val and (dx, dy) < best):
                    best_val = dist
                    best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]