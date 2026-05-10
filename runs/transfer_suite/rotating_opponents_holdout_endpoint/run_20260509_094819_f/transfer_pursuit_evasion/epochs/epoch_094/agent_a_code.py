def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    obs_list = []
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
                obs_list.append((x, y))

    sr = str(observation.get("self_role") or "").lower()
    pursuer = ("pursur" in sr) or ("chaser" in sr) or ("hunter" in sr) or ("pursuer" in sr) or ("tag" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_cell(x, y):
        if (x, y) in blocked:
            return -10**9 if pursuer else 10**9
        d = cheb(x, y, ox, oy)
        # obstacle proximity penalty
        adj = 0
        for bx, by in obs_list:
            if cheb(x, y, bx, by) == 0:
                return -10**9 if pursuer else 10**9
            if cheb(x, y, bx, by) == 1:
                adj += 1
        # edge penalty for evader to avoid being stuck
        edge = 0
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            edge = 1

        if pursuer:
            # minimize distance; strongly punish near blockers
            return -d * 20 - adj * 5 - edge * 2
        else:
            # maximize distance; avoid getting boxed in near blockers; slight central preference
            return d * 20 - adj * 6 - edge * 1

    # Deterministic tie-break: smallest dx, then dy, then order in moves list
    best_move = moves[0]
    best_score = score_cell(sx + moves[0][0], sy + moves[0][1])
    for dx, dy in moves[1:]:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
        elif sc == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]