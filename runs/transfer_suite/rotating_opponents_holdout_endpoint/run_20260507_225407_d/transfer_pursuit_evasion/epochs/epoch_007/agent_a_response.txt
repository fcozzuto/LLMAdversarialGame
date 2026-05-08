def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role) or ("catch" in opp_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        flee_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    else:
        flee_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        if is_pursuer:
            intercept = cheb(nx, ny, flee_corner[0], flee_corner[1])
            score = d + 0.15 * intercept
            t = (score, d, manh(nx, ny, ox, oy))
            if best is None or t < best:
                best = t
                best_move = [dx, dy]
        else:
            dist_from_opp = d
            toward_corner = cheb(nx, ny, flee_corner[0], flee_corner[1])
            # Evader: maximize distance to opponent, then maximize distance to opponent's flee corner proxy
            score = -dist_from_opp - 0.05 * toward_corner
            t = (score, -manh(nx, ny, ox, oy))
            if best is None or t < best:
                best = t
                best_move = [dx, dy]

    return best_move