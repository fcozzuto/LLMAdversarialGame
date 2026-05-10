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
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_key = None
    for rx, ry in res:
        sd = cheb((sx, sy), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        lead = od - sd  # positive means we are closer/earlier in this metric
        # Prefer contests; if no contest, fall back to nearest resource.
        contest_flag = 1 if lead > 0 else 0
        key = (contest_flag, lead, -sd, -(rx + ry), (-observation.get("turn_index", 0) & 1))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    turn = int(observation.get("turn_index", 0))
    pref1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    pref2 = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    moves_pref = pref1 if (turn & 1) == 0 else pref2

    best_move = (0, 0)
    best_dist = None
    for dx, dy in moves_pref:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = cheb((nx, ny), (tx, ty))
        if best_dist is None or d < best_dist:
            best_dist = d
            best_move = (dx, dy)
        elif d == best_dist:
            if (dx, dy) == (0, 0):
                continue
            if best_move == (0, 0):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]