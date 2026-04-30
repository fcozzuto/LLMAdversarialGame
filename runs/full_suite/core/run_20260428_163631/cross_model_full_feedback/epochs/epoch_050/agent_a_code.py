def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick target resource where we are more likely to secure it first.
    resources = list(set(resources))
    best_target = None
    best_val = None
    self_pos = (sx, sy)
    opp_pos = (ox, oy)
    for rx, ry in resources:
        dS = cheb(self_pos, (rx, ry))
        dO = cheb(opp_pos, (rx, ry))
        # Prefer: we are closer; also prefer closer absolute distances.
        val = (dO - dS) * 10 - dS
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    # If no resources, go to reduce distance to opponent to prevent contest? instead just hold.
    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    # Move choice: minimize distance to target, while penalizing being adjacent to opponent and entering bad contest.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        npos = (nx, ny)
        d_to_target = cheb(npos, (tx, ty))
        d_opp = cheb(npos, opp_pos)
        # Penalize moves that let opponent get significantly closer to the same target.
        dO_after = cheb(opp_pos, (tx, ty))
        # Opponent move is unknown; approximate by penalizing low opp distance to our next cell.
        adj_pen = 0
        if d_opp <= 1:
            adj_pen = 8
        # Extra: avoid moving away from target if opponent also near target.
        contest_pen = 0
        if cheb(self_pos, (tx, ty)) - cheb(opp_pos, (tx, ty)) < 0 and d_to_target > cheb(self_pos, (tx, ty)):
            contest_pen = 6
        score = -d_to_target * 3 - adj_pen - contest_pen
        # Deterministic tie-break: prefer staying if equal, else lowest dx, then lowest dy.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]