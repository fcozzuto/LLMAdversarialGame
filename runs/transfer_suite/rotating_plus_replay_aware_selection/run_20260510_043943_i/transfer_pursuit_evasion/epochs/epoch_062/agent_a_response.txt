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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            if (x + dx, y + dy) in obstacles:
                return 1
        return 0

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # approximate opponent best response (1-ply), then choose move that improves our objective
    def opp_best(nx, ny):
        best_val = None
        best = (ox, oy)
        for dx, dy in dirs:
            tx, ty = ox + dx, oy + dy
            if not valid(tx, ty):
                tx, ty = ox, oy
            d = cheb(nx, ny, tx, ty)
            # if opponent is evader, maximize distance; if opponent is pursuer, minimize distance
            val = d if not is_evader else -d
            # obstacle avoidance
            val += (-0.2 if adj_obs(tx, ty) else 0.0)
            if best_val is None or val > best_val:
                best_val = val
                best = (tx, ty)
        return best

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        tx, ty = opp_best(nx, ny)
        d2 = cheb(nx, ny, tx, ty)
        # objective: pursuer minimize, evader maximize
        score = (-d2 if not is_evader else d2)
        score += (-0.25 if adj_obs(nx, ny) else 0.0)
        score += (0.01 * (nx + ny))  # deterministic tie-break
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]