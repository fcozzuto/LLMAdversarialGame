def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_evader = ("evader" in role and "pursuer" not in role) or ("evader" in opp_role and "pursuer" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    # Deterministic tie-break prefers: maximize score, then prefer moves closer to staying still
    # and then lexicographic by (dx,dy).
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Simple one-step avoidance of getting "boxed": discourage moving into low-mobility cells when evading
        if is_evader:
            score = d * 100 + mob * 3
            # If adjacent, prefer breaking adjacency by increasing distance more strongly
            if cheb(nx, ny, ox, oy) <= 1:
                score -= (2 - d) * 200
        else:
            # Pursuer: reduce distance and avoid obstacles; also keep moving to maintain mobility
            score = (-d) * 100 + mob * 2

        if best_score is None or score > best_score or (score == best_score and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move