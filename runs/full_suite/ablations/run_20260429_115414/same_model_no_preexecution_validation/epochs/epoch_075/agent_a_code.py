def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target scoring: maximize (opponent advantage) and prefer nearer resources for us.
    best = None
    best_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # If we can reach sooner, strongly prefer; otherwise try to deny (do - ds).
        score = (do - ds) * 10 - ds
        # Small deterministic tie-breaker
        score2 = score * 1000 - (tx + ty * w)
        if best_score is None or score2 > best_score:
            best_score = score2
            best = (tx, ty)

    tx, ty = best

    # Choose best immediate move: maximize expected advantage after moving, with obstacle safety.
    best_m = (0, 0)
    best_m_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Also mildly account for keeping away from opponent to reduce contest loss.
        opp_dist = cheb(nx, ny, ox, oy)
        score = (no - ns) * 10 - ns + opp_dist * 0.1
        score2 = score * 1000 + (nx + ny * w) * 1e-6
        if best_m_score is None or score2 > best_m_score:
            best_m_score = score2
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]