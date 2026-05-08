def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evading = any(k in role for k in ("evade", "runner", "flee", "evasion", "evader"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def best_corner_toward(ex, ey):
        # point "toward" farthest corner for evasion, nearest corner for pursuit-cutoff
        if evading:
            return max(corners, key=lambda t: abs(t[0]-ex) + abs(t[1]-ey))
        return min(corners, key=lambda t: abs(t[0]-ex) + abs(t[1]-ey))
    def obst_pen(x, y):
        if (x, y) in obstacles: return 10**6
        # also discourage stepping near obstacles
        p = 0
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d == 0: return 10**6
            if d == 1: p += 5
            elif d == 2: p += 2
        return p

    def score_pos(x, y):
        d = cheb(x, y, ox, oy)
        corner = best_corner_toward(ox, oy)
        cc = cheb(x, y, corner[0], corner[1])
        # cutoff: for pursuer, reduce distance to opponent while also getting closer to the "escape-nearest" corner
        # runner: move toward farthest corner while keeping away from pursuer
        if evading:
            return 3.0 * d + 1.2 * cc - obst_pen(x, y)
        else:
            return -3.0 * d - 0.8 * cc - obst_pen(x, y)

    best = None
    bestv = None
    # deterministic tie-breaking by move order preference: stay, then N/S/E/W-ish, then diagonals
    pref = [(0,0), (0,-1), (0,1), (-1,0), (1,0), (-1,-1), (-1,1), (1,-1), (1,1)]
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        v = score_pos(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None: best = [0, 0]
    return best