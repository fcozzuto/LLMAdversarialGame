def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        best_move = (0, 0)
        best_val = -10**9
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -man(nx, ny, cx, cy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Target selection: prioritize resources where we are closer than opponent, then closeness.
    def move_value(nx, ny):
        best = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Gain is how much closer we are than opponent; discourage being too far.
            gain = od - sd
            val = gain * 10 - sd
            # Small tie-breakers favor resources nearer to our current axis/edge to counter edge_patrol.
            edge_bias = min(rx, w - 1 - rx) + min(ry, h - 1 - ry)
            val -= edge_bias * 0.1
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: prefer moves in fixed order, and smaller (abs(dx)+abs(dy)) for stability.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = move_value(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (abs(dx) + abs(dy)) < (abs(best_move[0]) + abs(best_move[1])):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]