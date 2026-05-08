def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            my_moves.append((dx, dy))
    if not my_moves:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            if free(x + dx, y + dy):
                c += 1
        return c

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_am_pursuer = ("pursuer" in srole) or ("catch" in srole) or ("chaser" in srole) or ("pursuit" in srole)
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if ("pursuer" in orole or "chaser" in orole or "catch" in orole or "pursuit" in orole) and not i_am_pursuer:
        i_am_pursuer = True

    opp_moves = []
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if free(nx, ny):
            opp_moves.append((dx, dy))
    if not opp_moves:
        opp_moves = [(0, 0)]

    best = None
    best_score = None
    for dx, dy in my_moves:
        nx, ny = sx + dx, sy + dy
        if i_am_pursuer:
            worst = -1
            for odx, ody in opp_moves:
                tox, toy = ox + odx, oy + ody
                worst = max(worst, dist2(nx, ny, tox, toy))
            score = (-worst, mobility(nx, ny))
        else:
            bestd = 10**18
            for odx, ody in opp_moves:
                tox, toy = ox + odx, oy + ody
                bestd = min(bestd, dist2(nx, ny, tox, toy))
            score = (bestd, mobility(nx, ny))
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    return [best[0], best[1]]