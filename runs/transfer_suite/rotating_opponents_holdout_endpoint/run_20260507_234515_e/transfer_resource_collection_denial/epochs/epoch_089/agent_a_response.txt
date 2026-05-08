def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick a target resource where we can arrive earlier (maximize lead).
    best_res = resources[0]
    best_lead = -10**18
    best_selfd = 10**9
    for rx, ry in resources:
        rx = int(rx); ry = int(ry)
        selfd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        lead = oppd - selfd
        if lead > best_lead or (lead == best_lead and selfd < best_selfd):
            best_lead = lead
            best_selfd = selfd
            best_res = [rx, ry]

    rx, ry = best_res
    # If we are behind everywhere, shift to minimizing opponent distance to the chosen target.
    all_behind = True
    for r2x, r2y in resources:
        r2x = int(r2x); r2y = int(r2y)
        if cheb(sx, sy, r2x, r2y) <= cheb(ox, oy, r2x, r2y):
            all_behind = False
            break

    best_move = [0, 0]
    best_val = -10**18
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        selfd2 = cheb(nx, ny, rx, ry)
        oppd2 = cheb(ox, oy, rx, ry)  # opp position static this turn
        if all_behind:
            val = -oppd2  # try to reduce our chance to get blocked off from the best target
        else:
            val = oppd2 - selfd2
        if val > best_val or (val == best_val and selfd2 < best_dist):
            best_val = val
            best_dist = selfd2
            best_move = [dx, dy]

    return best_move