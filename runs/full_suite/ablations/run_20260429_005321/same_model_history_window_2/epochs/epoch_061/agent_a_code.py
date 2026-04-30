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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_ob_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2 if (dx != 0 and dy != 0) else 1
        return pen

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx = 0 if sx < ox else w - 1
        ty = 0 if sy < oy else h - 1
        resources = [(tx, ty)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        step_pen = 0
        step_pen += 3 * adj_ob_pen(nx, ny)
        # Block / race: prefer tiles that move us closer to resources before opponent.
        # Score: opponent-advantage + mild resource preference.
        val = step_pen
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            race = do - ds  # positive => we are closer
            # Tie-break deterministically toward upper-left resource
            tie = -0.001 * (rx * 100 + ry)
            val += -(race * 10 + tie)
        # Prefer moving that also reduces our distance to the best resource
        # by selecting minimal total distance difference.
        min_diff = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
            if min_diff is None or d < min_diff:
                min_diff = d
        val += min_diff * 2
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]