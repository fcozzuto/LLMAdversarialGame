def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    # Simple path-safety: penalize moves that move closer to obstacles by distance-1 adjacency.
    obst_adj = set()
    for (x, y) in blocked:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                obst_adj.add((nx, ny))

    opp_next_bonus = 1  # opponent can reduce distance by about 1 on their turn

    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in resources:
            return [dx, dy]
        my_adv_sum = None
        # Evaluate best achievable resource race for this move.
        # Prefer minimizing (our_dist - opponent_dist_after_one_step) and also overall our distance.
        best_for_move = None
        for rx, ry in resources:
            d_my = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # If opponent could get there sooner, penalize heavily.
            # opponent after one step approximation: distance reduces by 1 but not below 0
            d_op1 = d_op - opp_next_bonus
            if d_op1 < 0: d_op1 = 0
            # Lower is better: want to be closer than opponent, and also closer in absolute terms.
            race = d_my - d_op1
            # Extra penalty if resource is adjacent to obstacles (more likely to contest)
            adj_res = 0
            for ddx, ddy in moves:
                tx, ty = rx + ddx, ry + ddy
                if (tx, ty) in blocked:
                    adj_res = 1
                    break
            val = (race, d_my + 2 * adj_res)
            if best_for_move is None or val < best_for_move:
                best_for_move = val
        # Combine: prefer move with smallest best_for_move tuple, then avoid obstacle-adjacent squares.
        if best_for_move is None:
            continue
        obst_pen = 1 if (nx, ny) in obst_adj else 0
        total = (best_for_move[0], best_for_move[1] + 3 * obst_pen, -man(nx, ny, ox, oy))
        if best_val is None or total < best_val:
            best_val = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]