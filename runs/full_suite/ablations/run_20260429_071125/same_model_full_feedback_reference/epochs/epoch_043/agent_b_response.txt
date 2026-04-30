def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        candidates = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer or ties
            if lead > -5:
                candidates.append((lead, -ds, rx, ry))
        candidates.sort(reverse=True)
        rx, ry = (candidates[0][2], candidates[0][3]) if candidates else (resources[0][0], resources[0][1])
    else:
        rx, ry = (w // 2, h // 2)

    best = (None, -10**9, 10**9, 10**9)  # move, score, self_d, opp_d
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer reducing our distance to the chosen target, and if possible widen our lead.
        lead_after = opp_d - self_d
        score = lead_after * 1000 - self_d
        # Small tie-break: prefer moving closer to the center when target offers no improvement.
        if resources == []:
            cx, cy = w // 2, h // 2
            score += -cheb(nx, ny, cx, cy)
        if score > best[1] or (score == best[1] and (self_d < best[2] or (self_d == best[2] and opp_d < best[3]))):
            best = ((dx, dy), score, self_d, opp_d)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]