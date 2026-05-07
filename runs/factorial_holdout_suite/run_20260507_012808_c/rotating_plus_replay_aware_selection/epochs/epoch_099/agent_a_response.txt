def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18
    res = [tuple(r) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; otherwise prefer denying (opp closer).
            advantage = opp_d - our_d
            s = advantage * 1000 - our_d
            # Slightly prefer closer overall resources to reduce tie issues deterministically.
            if (our_d == 0) and (opp_d > 0):
                s += 10**6
            move_score = s if s > move_score else move_score
        # Deterministic tie-break: prefer smaller our distance to the best resource, then lexicographic move.
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
        elif move_score == best_score:
            if (best_move == [0, 0] and [dx, dy] != [0, 0]) or (cheb(nx, ny, res[0][0], res[0][1]) < cheb(sx + best_move[0], sy + best_move[1], res[0][0], res[0][1])):
                best_move = [dx, dy]
            elif [dx, dy] < best_move:
                best_move = [dx, dy]
    if not valid(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move