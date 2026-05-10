def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for b in observation.get("obstacles", []) or []:
        try:
            obs.add((int(b[0]), int(b[1])))
        except:
            pass

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def valid(x, y): return inb(x, y) and not blocked(x, y)
    def move(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        return (nx, ny) if valid(nx, ny) else (x, y)
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    def greedy_evader(px, py, ex, ey):
        best = (px, py)
        bestv = -10**18
        for dx, dy in actions:
            nx, ny = move(px, py, dx, dy)
            v = dist2(nx, ny, ex, ey)
            if v > bestv:
                bestv = v
                best = (nx, ny)
        return best

    def greedy_pursuer(ex, ey, px, py):
        best = (ex, ey)
        bestv = 10**18
        for dx, dy in actions:
            nx, ny = move(ex, ey, dx, dy)
            v = dist2(nx, ny, px, py)
            if v < bestv:
                bestv = v
                best = (nx, ny)
        return best

    # One-step lookahead: if we are pursuer, opponent likely evades; else we likely get chased.
    best_move = (0, 0)
    best_score = -10**18 if pursuer else 10**18
    for dx, dy in actions:
        nx, ny = move(sx, sy, dx, dy)
        if pursuer:
            ne_x, ne_y = greedy_evader(ox, oy, nx, ny)
            score = -dist2(nx, ny, ne_x, ne_y)
            # small bias: avoid getting stuck against obstacles
            if (nx, ny) == (sx, sy): score -= 0.01
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            np_x, np_y = greedy_pursuer(nx, ny, ox, oy)
            score = dist2(nx, ny, np_x, np_y)
            if (nx, ny) == (sx, sy): score -= 0.01
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]