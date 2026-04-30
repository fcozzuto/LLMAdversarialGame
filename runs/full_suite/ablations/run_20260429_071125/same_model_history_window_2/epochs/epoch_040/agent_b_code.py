def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        our_min = 10**9
        opp_min = 10**9
        our_second = 10**9
        opp_threat = 0
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            if d_our < our_min:
                our_second = our_min
                our_min = d_our
            elif d_our < our_second:
                our_second = d_our
            d_opp = cheb(ox, oy, rx, ry)
            if d_opp < opp_min:
                opp_min = d_opp

        # Encourage closeness to a resource, discourage letting opponent be closer.
        # Also slightly prefer moves that keep us away from obstacles edges (soft).
        score = 0.0
        score += 50.0 / (1.0 + our_min)
        score += 8.0 / (1.0 + our_second)
        if opp_min < 10**9:
            gap = opp_min - our_min
            score += 12.0 * gap  # positive if we're closer

        # Soft obstacle penalty: stay with more open local space
        local_free = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    local_free += 1
        score += 0.2 * local_free

        # Tie-break deterministically
        if score > best_score + 1e-12 or (abs(score - best_score) <= 1e-12 and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]