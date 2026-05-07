def choose_move(observation):
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    gw, gh = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh
    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer grabbing when we are (eventually) closer; otherwise deny by moving toward contested cells.
    if resources:
        best = [0, 0]
        bestv = -10**18
        # Opponent position known; use it only for relative timing.
        ox, oy = observation["opponent_position"]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v_best = -10**18
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Strongly prefer resources where we arrive no later than opponent.
                advantage = d_opp - d_me
                v = (1000 if advantage >= 0 else 0) + advantage * 10 - d_me
                if v > v_best:
                    v_best = v
            if v_best > bestv:
                bestv = v_best
                best = [dx, dy]
        return best

    # No visible resources: drift toward the nearest free corner away from obstacles.
    target_corners = []
    if sx < gw // 2 and sy < gh // 2:
        target_corners = [(0, gh - 1), (gw - 1, gh - 1)]
    elif sx >= gw // 2 and sy < gh // 2:
        target_corners = [(gw - 1, gh - 1), (0, gh - 1)]
    elif sx < gw // 2 and sy >= gh // 2:
        target_corners = [(0, 0), (gw - 1, 0)]
    else:
        target_corners = [(gw - 1, 0), (0, 0)]

    tx, ty = None, None
    for cx, cy in target_corners:
        if legal(cx, cy) or True:
            tx, ty = cx, cy
            break
    if tx is None:
        tx, ty = 0, 0

    best, bestv = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = -cheb(nx, ny, tx, ty)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best