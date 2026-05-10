def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    my_best_res = None
    my_best_d = 10**9
    for rx, ry in resources:
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if d < my_best_d:
            my_best_d = d
            my_best_res = (rx, ry)

    def eval_move(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        # Pick best resource from this position, weighted against opponent proximity.
        best_val = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                return 10**9  # immediate collection
            myd = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            opd = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            # If opponent is closer, penalize; if farther, reward more.
            rel = (opd - myd)
            val = 1.8 * rel - 0.15 * myd
            # Subtle obstacle aversion: discourage stepping adjacent to obstacles.
            if obstacles:
                for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (nx + ax, ny + ay) in obstacles:
                        val -= 0.35
            best_val = max(best_val, val)
        # Small preference to keep heading toward the currently closest resource.
        if my_best_res is not None:
            rx, ry = my_best_res
            best_val += -0.03 * ((rx - nx) * (rx - nx) + (ry - ny) * (ry - ny))
        return best_val

    best_score = -10**18
    best_move = [0, 0]
    # Deterministic tie-break order: prioritize moves that reduce dx/dy magnitude toward resources.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = eval_move(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
        elif sc == best_score:
            # Tie-break: prefer the move with smallest squared distance to nearest resource from new position.
            cand = None
            for rx, ry in resources:
                d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
                if cand is None or d < cand:
                    cand = d
            cur = None
            ox2, oy2 = sx + best_move[0], sy + best_move[1]
            for rx, ry in resources:
                d = (rx - ox2) * (rx - ox2) + (ry - oy2) * (ry - oy2)
                if cur is None or d < cur:
                    cur = d
            if cand is not None and cur is not None and cand < cur:
                best_move = [dx, dy]

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]