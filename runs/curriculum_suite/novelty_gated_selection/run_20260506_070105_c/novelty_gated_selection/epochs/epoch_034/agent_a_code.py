def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx = sy = ox = oy = 0

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obs = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    res = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
        except Exception:
            pass

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_sc = -10**18
    cur_near = min((md(sx, sy, rx, ry) for rx, ry in res), default=10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (dx, dy) == (0, 0) and res and cur_near == 0:
            sc = 10**6
        else:
            near = min((md(nx, ny, rx, ry) for rx, ry in res), default=10**9)
            sc = -near + 0.15 * md(nx, ny, ox, oy)
            if (nx, ny) in set(res):
                sc += 10**6
            if ox != sx or oy != sy:
                # small anti-approach to opponent unless we can capture
                sc -= 0.05 * (md(nx, ny, ox, oy) <= md(sx, sy, ox, oy))
        if sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1]) if best else False):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]