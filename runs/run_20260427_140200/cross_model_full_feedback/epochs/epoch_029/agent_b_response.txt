def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def dist_cheb(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    # Build candidate moves that stay within bounds and not on obstacle
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Score each candidate: prefer moving toward closest resource, then away from opponent
    best = None
    best_score = None

    for dx, dy, nx, ny in cand:
        score = 0.0

        # Resource proximity
        if resources:
            d_r = min(dist_cheb(nx, ny, rx, ry) for rx, ry in resources)
            score -= 1.0 * d_r * 0.5  # prefer closer to resources

        # Opponent danger: prefer increasing distance or maintaining safe gap
        d_opp = dist_cheb(nx, ny, ox, oy)
        score += d_opp * 0.6  # keep distance

        # Center bias: slight preference toward center to avoid edges
        cx, cy = w / 2, h / 2
        score += -abs(nx - cx) * 0.05 - abs(ny - cy) * 0.05

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]