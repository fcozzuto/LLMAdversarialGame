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
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        key = (opp_d - self_d, -self_d, -cx, -cy)
        if best_key is None or key > best_key:
            best_key, best = key, (cx, cy)

    # If we aren't currently closer (advantage <= 0), switch to nearest-to-us resource.
    if best_key and best_key[0] <= 0:
        best = min(resources, key=lambda c: (cheb(sx, sy, c[0], c[1]), c[0], c[1]))

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d2 = cheb(nx, ny, tx, ty)
        opp_d2 = cheb(ox, oy, tx, ty)
        # We assume opponent may also act; reward moves that keep us relatively better.
        score = (opp_d2 - self_d2, -self_d2, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]