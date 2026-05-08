def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer corners in a deterministic rotating pattern (materially different from simple flee).
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    far_corner_from_opp = corners[phase]
    best_corner_score = -10**9
    for c in corners:
        s = cheb(c[0], c[1], ox, oy)
        if s > best_corner_score:
            best_corner_score = s
            far_corner_from_opp = c

    def obstacle_cost(x, y):
        # Small deterministic avoidance: adjacent is bad, very close is worst.
        c = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10**7
            if d == 1:
                c += 120
            elif d == 2:
                c += 25
            elif d == 3:
                c += 8
        return c

    def score_next(x, y):
        d = cheb(x, y, ox, oy)
        # Edge bias: encourage evader toward outer boundary to limit pursuit routes.
        edge = min(x, y, w - 1 - x, h - 1 - y)
        edge_bonus = (w + h) - 2 * edge  # larger near boundary
        oc = obstacle_cost(x, y)
        if is_evader:
            # Maximize distance, then push toward a far corner, but avoid obstacles.
            corner_d = cheb(x, y, far_corner_from_opp[0], far_corner_from_opp[1])
            return d * 1000 + corner_d * 50 + edge_bonus * 10 - oc
        else:
            # Pursuer: minimize distance to evader; also avoid obstacles.
            return -d * 1000 + edge_bonus * 2 - oc

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_next(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]