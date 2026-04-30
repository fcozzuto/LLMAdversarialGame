def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer reachable advantage; break ties by nearer self and farther opponent.
            gap = od - sd
            key = (gap, -sd, od, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    sd0 = cheb(sx, sy, tx, ty)
    od0 = cheb(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Main: decrease self distance, keep opponent from getting advantage.
        # Secondary: don't oscillate; prefer moves that also reduce distance to target.
        d_self_improve = sd0 - sd
        opp_pressure = od - sd  # larger means self closer relative to opponent
        stay_pen = 1 if (nx == sx and ny == sy) else 0
        resource_here_bonus = 2 if (nx, ny) == (tx, ty) else 0
        score = (d_self_improve * 3) + (opp_pressure * 2) + (resource_here_bonus) - (stay_pen)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]