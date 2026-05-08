def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)
    res_list = observation.get("resources", []) or []
    resources = [tuple(p) for p in res_list]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    want_escape = False
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    if any(k in role for k in ("evade", "runner", "flee", "evasion", "evader")):
        want_escape = True

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0

        if resources:
            best_r = 10**9
            for rx, ry in resources:
                d = dist_cheb(nx, ny, rx, ry)
                if d < best_r:
                    best_r = d
            score += 50 - 5 * best_r

        dob = dist_cheb(nx, ny, ox, oy)
        if want_escape:
            score += 8 * dob - 2
            if dob <= 1:
                score -= 30
        else:
            score += -2 * dob
            if dob <= 1:
                score += 20

        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if in_bounds(ax, ay) and (ax, ay) in obstacles:
                score -= 2

        score += (0 if dx == 0 and dy == 0 else 0)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]