def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves9 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None
    for rx, ry in res:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        score = (od - sd, -sd, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)
    tx, ty = best

    def step_options():
        dx = 0
        if tx > sx: dx = 1
        elif tx < sx: dx = -1
        dy = 0
        if ty > sy: dy = 1
        elif ty < sy: dy = -1
        pref = []
        if dx != 0 and dy != 0:
            pref.append((dx, dy))
        if dx != 0:
            pref.append((dx, 0))
        if dy != 0:
            pref.append((0, dy))
        pref.append((0, 0))
        out = []
        for d in pref:
            out.append(d)
        for d in moves9:
            if d not in out:
                out.append(d)
        return out

    target_dist = dist((sx, sy), (tx, ty))
    options = step_options()
    best_move = (0, 0)
    best_move_score = None
    for mx, my in options:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs:
            continue
        nd = dist((nx, ny), (tx, ty))
        improvement = target_dist - nd
        score = (improvement, -nd, mx, my)
        if best_move_score is None or score > best_move_score:
            best_move_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]