def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                rlist.append((rx, ry))
    if not rlist:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                if md(nx, ny, tx, ty) <= md(sx, sy, tx, ty):
                    return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0.0
        self_d0 = 999
        for rx, ry in rlist:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            self_d0 = min(self_d0, ds)
            if ds <= do:
                score += 10.0 - ds
            else:
                gap = do - ds
                score += -0.2 * ds - 1.0 * gap
        # tie-breakers: prefer closer to any resource, then closer to opponent (slight disrupt), then smaller dx/dy lex
        tie = ( -self_d0, -md(nx, ny, ox, oy), dx, dy )
        cur = (score, tie)
        if best_score is None or cur > best_score:
            best_score = cur
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]