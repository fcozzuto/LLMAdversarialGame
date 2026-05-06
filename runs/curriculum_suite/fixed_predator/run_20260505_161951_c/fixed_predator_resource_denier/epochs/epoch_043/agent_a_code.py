def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))
        elif isinstance(o, dict) and "x" in o and "y" in o:
            obs.add((int(o["x"]), int(o["y"])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)

        if res:
            bd = 10**9
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if d < bd:
                    bd = d
            v = (bd == 0) * 10**6 + (-bd) * 50 + d_opp * 3
        else:
            tx, ty = w - 1, h - 1
            v = -cheb(nx, ny, tx, ty) * 5 + d_opp * 3

        if v > bestv:
            bestv = v
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]