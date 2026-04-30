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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            val = cheb(nx, ny, tx, ty)
            if val < best[0] or (val == best[0] and (nx, ny) < best[2]):
                best = (val, 0, (nx, ny))
        return [best[2][0] - sx, best[2][1] - sy]

    best_move = None
    best_score = None

    # Deterministic scoring: attack resources where we're closer than opponent; otherwise reduce opponent advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        worst = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If opponent can reach sooner, penalize strongly; else reward.
            val = (d_me - d_op) * 3 + d_me
            # Slight preference for nearer target to us even when contested
            if worst is None or val > worst:
                worst = val
        # Lower is better. Tie-break by lexicographic position.
        score = worst
        if best_score is None or score < best_score or (score == best_score and (nx, ny) < best_move):
            best_score = score
            best_move = (nx, ny)

    return [best_move[0] - sx, best_move[1] - sy]