def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs_score(x, y):
        cnt = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                cnt += 1
        return -2 * cnt

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic "escape" from obstacles / drift to center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, tx, ty) + near_obs_score(nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        # Opponent-aware pursuit: prefer resources we can reach no later than opponent,
        # and if ahead, prioritize the biggest lead; otherwise minimize our distance while
        # not giving the opponent an advantage.
        move_val = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # We also approximate opponent after our move (small bias to reduce race ties)
            # by assuming opponent holds position; that's deterministic and cheap.
            if ds <= do:
                v = (do - ds) * 10 - ds - (cheb(nx, ny, sx, sy) * 0) + near_obs_score(nx, ny)
            else:
                # If behind, avoid it unless it's the only close option.
                v = -(ds - do) * 6 - ds + near_obs_score(nx, ny)
            move_val = v if move_val is None else (move_val + v) * 0.0 + (v if v > move_val else move_val)
        # Deterministic tie-break: prefer moves that decrease our distance to closest resource
        if move_val is None:
            move_val = -10**9
        closest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        vtot = move_val * 1000 - closest
        if bestv is None or vtot > bestv:
            bestv = vtot
            best = (dx, dy)

    return [best[0], best[1]]