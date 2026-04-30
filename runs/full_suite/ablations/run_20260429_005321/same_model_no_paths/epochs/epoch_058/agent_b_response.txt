def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand_moves.append((dx, dy, nx, ny))
    if not cand_moves:
        return [0, 0]

    # Deterministic shift: sometimes prioritize contesting resources closer to opponent line
    # by blending (opp_dist - self_dist) with an "interception" term.
    top_resources = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))[:6]

    best = None
    best_score = None
    idx_bias = int(observation.get("turn_index") or 0) % 2

    for dx, dy, nx, ny in cand_moves:
        score = None
        for i, (tx, ty) in enumerate(top_resources):
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # If we can arrive not later than opponent, strong.
            # Prefer smaller own distance, and resources that reduce opponent advantage.
            advantage = do - ds
            intercept = 0
            # Interception term: move that reduces our distance to the segment toward opponent.
            # Use opponent-relative Chebyshev projection.
            step_towards_opp = cheb(nx, ny, ox, oy)
            intercept = -step_towards_opp * (0.02 + 0.01 * ((i + idx_bias) % 3))
            s = advantage * 10.0 - ds * 1.0 + intercept
            if score is None or s > score:
                score = s
        # Tie-break deterministically: lexicographic on (dx,dy) after score.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]