def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    res_list = observation.get("resources") or []
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Pick move that maximizes (opponent advantage) for the best reachable resource after the move.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            nx, ny = x, y

        # Evaluate best resource from this hypothetical position.
        local_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources where we are closer; also strongly prefer where we swing turn-order.
            v = (od - sd) * 1000 - sd
            # Small tie-break toward not wandering from current opponent-frontier.
            if od == sd:
                v -= sd // 2
            if v > local_best:
                local_best = v

        # Add mild preference to reduce distance to chosen best target area.
        # Deterministic proxy: keep sum of distances low.
        proxy = 0
        for rx, ry in resources:
            proxy += md(nx, ny, rx, ry)
            break

        val = local_best - proxy * 0.0001
        if val > best_val:
            best_val = val
            best_move = (dx if ok(x + dx, y + dy) else 0, dy if ok(x + dx, y + dy) else 0)

    return [int(best_move[0]), int(best_move[1])]