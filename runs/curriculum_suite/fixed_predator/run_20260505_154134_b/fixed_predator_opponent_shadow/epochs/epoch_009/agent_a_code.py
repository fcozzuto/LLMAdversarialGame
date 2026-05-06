def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_cell = None
    best_score = -10**18
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # Prefer cells we are closer to; break ties toward nearer resources
        sc = (opp_d - self_d) * 1000 - self_d
        if sc > best_score:
            best_score = sc
            best_cell = (cx, cy)

    cx, cy = best_cell
    # Aim directly toward the chosen cell, but allow obstacle avoidance
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Higher is better
        to_cell = cheb(nx, ny, cx, cy)
        opp_to_cell = cheb(ox, oy, cx, cy)
        # Prefer reducing our distance to the cell and not getting closer to opponent more than necessary
        v = (opp_to_cell - to_cell) * 1000 - to_cell + cheb(nx, ny, ox, oy) * 2
        cand.append((v, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (t[0], -t[1], -t[2]), reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]