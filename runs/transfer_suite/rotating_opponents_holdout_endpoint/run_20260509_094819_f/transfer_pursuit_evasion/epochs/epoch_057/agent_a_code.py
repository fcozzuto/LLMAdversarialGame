def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "").lower()
    i_am_pursuer = ("purs" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    target_x, target_y = ox, oy
    if not i_am_pursuer:
        best_corner = (sx, sy)
        best_d = -1
        for cx, cy in corners:
            if (cx, cy) in blocked:
                continue
            d = cheb(cx, cy, ox, oy)
            if d > best_d:
                best_d = d
                best_corner = (cx, cy)
        target_x, target_y = best_corner

    best_move = (0, 0)
    best_score = None
    # Tie-break deterministically by the fixed moves order
    if i_am_pursuer:
        # minimize distance to opponent
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = (-d, -(abs(nx - ox) + abs(ny - oy)))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # maximize distance from pursuer (and prefer moving toward chosen far corner if equal)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_away = cheb(nx, ny, ox, oy)
            d_to_corner = cheb(nx, ny, target_x, target_y)
            score = (d_away, -d_to_corner)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]