def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    env = (observation.get("environment_name") or "").lower()

    i_am_pursuer = ("pursuer" in self_role and "evader" not in self_role) or ("pursuit" in env and "evader" not in self_role)
    if not i_am_pursuer and ("evader" in self_role):
        i_am_pursuer = False
    # if still ambiguous, infer from opponent_role if possible
    if "pursuer" in opp_role and "evader" not in opp_role:
        i_am_pursuer = False

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    def dist2(x, y, x2, y2):
        dx, dy = x - x2, y - y2
        return dx * dx + dy * dy

    def obs_proximity(x, y):
        # small penalty near obstacles to avoid getting "wall trapped"
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    return 1
        return 0

    def edge_risk(x, y):
        # avoid boundary sticking for evader; for pursuer helps not to waste moves
        return (x == 0) or (x == w - 1) or (y == 0) or (y == h - 1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        prox = obs_proximity(nx, ny)
        edge = 1 if edge_risk(nx, ny) else 0

        if i_am_pursuer:
            # minimize distance; tie-breaker: reduce Manhattan; avoid obstacle adjacency (wall-run)
            score = (d2, man, prox, edge, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # maximize distance; tie-breaker: increase Manhattan; avoid obstacle adjacency to escape
            score = (-d2, -man, -prox, -edge, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]