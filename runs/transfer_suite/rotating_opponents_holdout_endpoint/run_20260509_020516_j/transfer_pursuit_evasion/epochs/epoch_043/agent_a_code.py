def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def man(x, y): return abs(x - ox) + abs(y - oy)
    def legal(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    base_corner = None
    best_corner_d = -10**9
    for cx, cy in corners:
        d = man(cx, cy)
        if d > best_corner_d:
            best_corner_d = d
            base_corner = (cx, cy)

    tx, ty = base_corner
    best_move = (0, 0)
    best_score = -10**18 if is_evader else 10**18
    curd = man(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = man(nx, ny)
        towards_corner = -((abs(nx - tx) + abs(ny - ty)) + 0.1 * (abs(nx - tx) > 0 and abs(ny - ty) > 0))
        if is_pursuer:
            # Prefer decreasing distance; slight preference for keeping obstacles at bay by discouraging low mobility
            mobility = 0
            for ddx, ddy in moves:
                ax, ay = nx + ddx, ny + ddy
                if legal(ax, ay):
                    mobility += 1
            score = (nd, -mobility, -abs(nx - ox), -abs(ny - oy))
            if score < (best_score if isinstance(best_score, tuple) else (best_score, 0, 0, 0)):
                best_score = score
                best_move = (dx, dy)
        else:
            # Prefer increasing distance from pursuer; if tied, go to farthest corner while not getting stuck
            mobility = 0
            for ddx, ddy in moves:
                ax, ay = nx + ddx, ny + ddy
                if legal(ax, ay):
                    mobility += 1
            score = (-nd, -abs(nx - tx) - abs(ny - ty), -(nd - curd), -mobility, towards_corner)
            if score > (best_score if isinstance(best_score, tuple) else (-best_score, 0, 0, 0)):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]