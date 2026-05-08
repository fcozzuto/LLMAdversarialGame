def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    env = str(observation.get("environment_name", "")).lower()
    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in env:
        if ("evad" in sr) or ("escape" in sr) or ("runner" in sr):
            is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    if is_pursuer:
        # Greedy chase: minimize chebyshev distance; tie-break by closer Euclid-ish and toward opponent vector
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            cd = cheb(nx, ny, ox, oy)
            ex = nx - ox
            ey = ny - oy
            e2 = ex * ex + ey * ey
            # vector alignment: prefer moves that generally head toward opponent (sign match)
            ax = 1 if ox > sx else (-1 if ox < sx else 0)
            ay = 1 if oy > sy else (-1 if oy < sy else 0)
            align = (dx == ax) + (dy == ay)
            score = (cd, e2, -align)
            if best is None or score < best[0]:
                best = (score, [dx, dy])
    else:
        # Greedy evade: maximize chebyshev distance; tie-break by maximizing squared distance and staying away from walls
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            cd = cheb(nx, ny, ox, oy)
            ex = nx - ox
            ey = ny - oy
            e2 = ex * ex + ey * ey
            # wall-avoid: prefer higher minimum margin to border
            wall_margin = nx if nx < (w - 1 - nx) else (w - 1 - nx)
            wall_margin2 = ny if ny < (h - 1 - ny) else (h - 1 - ny)
            wall = wall_margin if wall_margin < wall_margin2 else wall_margin2
            score = (-cd, -e2, -wall)
            if best is None or score < best[0]:
                best = (score, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]