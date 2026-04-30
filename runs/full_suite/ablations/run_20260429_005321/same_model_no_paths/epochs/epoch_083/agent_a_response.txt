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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_rx, best_ry = sx, sy
    best_adv = -10**9
    if resources:
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # tie-break: prioritize closer targets when advantage equal
            if adv > best_adv or (adv == best_adv and sd < cheb(sx, sy, best_rx, best_ry)):
                best_adv, best_rx, best_ry = adv, rx, ry
        # if we are far behind everyone, still go to the nearest resource (fallback)
        if best_adv < 0:
            mn = None
            for rx, ry in resources:
                sd = cheb(sx, sy, rx, ry)
                if mn is None or sd < mn:
                    mn = sd
                    best_rx, best_ry = rx, ry

    # Greedy move: minimize distance to chosen resource; include slight pressure vs opponent
    target_dist = cheb(sx, sy, best_rx, best_ry)
    best_move = [0, 0]
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = cheb(nx, ny, best_rx, best_ry)
        d_to_o = cheb(nx, ny, ox, oy)
        # primary: reduce distance to target; secondary: keep some distance from opponent
        score = (d_to_t * 1000) - (d_to_o * 5)
        # prefer making progress; if stuck, allow equal
        if d_to_t < target_dist or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move