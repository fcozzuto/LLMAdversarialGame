def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    best_move = (0, 0, -10**18)
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        # Target with maximum "win advantage": (opp_dist - my_dist), tie-break toward closer.
        best_adv = -10**18
        best_d = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv or (adv == best_adv and myd < best_d):
                best_adv = adv
                best_d = myd
        # Extra: don't step into cells that increase distance to current best resource excessively.
        # Deterministic tie-break: prefer diagonal when equal.
        diag = 1 if mdx != 0 and mdy != 0 else 0
        score = best_adv * 1000 - best_d + diag * 0.1
        if score > best_move[2]:
            best_move = (mdx, mdy, score)
    if best_move[2] <= -10**17:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]