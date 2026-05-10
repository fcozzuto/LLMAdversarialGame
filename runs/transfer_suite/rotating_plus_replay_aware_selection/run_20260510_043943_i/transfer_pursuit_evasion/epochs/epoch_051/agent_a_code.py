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
    role_opp = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role_self) or (role_opp and ("evader" in role_opp)) or ("chaser" in role_self) or ("hunter" in role_self)
    # If ambiguous: assume we are pursuer when opponent role says evader; else evader.

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    cx = sx + (sx - ox)
    cy = sy + (sy - oy)
    if cx < 0: cx = 0
    if cx > w - 1: cx = w - 1
    if cy < 0: cy = 0
    if cy > h - 1: cy = h - 1

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_best(x, y):
        best = -1
        for tx, ty in corners:
            d = cheb(x, y, tx, ty)
            if d > best: best = d
        return best

    best_move = (0, 0)
    if pursuer:
        # Intercept by chasing the square beyond opponent relative to us; fallback to direct chase.
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d_int = cheb(nx, ny, cx, cy)
            d_dir = cheb(nx, ny, ox, oy)
            # primary: minimize intercept distance, secondary: minimize direct distance, tertiary: prefer being on same row/col
            score = (d_int, d_dir, -(abs((nx - ox)) + abs((ny - oy))) )
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # Evader: maximize distance from pursuer; tie-break toward farthest corner.
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            corner = corner_best(nx, ny)
            # primary: maximize distance; secondary: maximize corner progress; tertiary: prefer move that doesn't reduce lexicographically
            score = (-d, -corner, -(nx + ny))
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]