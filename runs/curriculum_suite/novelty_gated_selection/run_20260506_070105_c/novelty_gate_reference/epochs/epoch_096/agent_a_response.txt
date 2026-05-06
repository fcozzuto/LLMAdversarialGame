def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target selection: prefer resources where we are (meaningfully) closer than opponent.
    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # higher is better; opponent-denier => prioritize winning race (do - ds)
        score = (do - ds) * 10 - ds
        # tie-break deterministically by lexicographic (rx, ry)
        if best is None or score > best_score or (score == best_score and (rx, ry) < best):
            best = (rx, ry)
            best_score = score
    tx, ty = best

    # Evaluate all candidate moves (including stay), reject invalid by staying.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Move score: progress to target, small preference to not overshoot and to improve over staying.
    best_move = None
    best_move_score = None
    for dx, dy, nx, ny in candidates:
        before = cheb(sx, sy, tx, ty)
        after = cheb(nx, ny, tx, ty)
        step_prog = before - after
        # also reward picking up if we land on a resource
        on_res = 1 if (nx, ny) in set(resources) else 0
        # mild repulsion from opponent to counter denial
        opp_dist = cheb(nx, ny, ox, oy)
        opp_term = opp_dist // 2
        score = step_prog * 100 + on_res * 1000 + opp_term
        if best_move is None or score > best_move_score or (score == best_move_score and (dx, dy) < best_move):
            best_move = (dx, dy)
            best_move_score = score
    return [int(best_move[0]), int(best_move[1])]