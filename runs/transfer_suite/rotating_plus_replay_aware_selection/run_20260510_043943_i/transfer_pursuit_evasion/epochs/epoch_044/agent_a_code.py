def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corner_bias(x, y):
        # for evader: prefer farthest corner; for pursuer: prefer nearest corner to opponent (cut off)
        if is_evader:
            best = -1
            for cx, cy in corners:
                d = cheb(x, y, cx, cy)
                if d > best: best = d
            return best
        else:
            best = 10**9
            for cx, cy in corners:
                d = cheb(cx, cy, ox, oy)
                if d < best: best = d
            return -best

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        dist = cheb(nx, ny, ox, oy)
        if is_evader:
            # maximize distance; also prefer moving toward a good corner when it doesn't reduce distance
            score = dist * 100 - (abs(nx - sx) + abs(ny - sy)) + corner_bias(nx, ny)
        else:
            # minimize distance; slight preference for reducing opponent's access to corners (via our corner_bias)
            score = -dist * 100 - (abs(nx - sx) + abs(ny - sy)) + corner_bias(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move