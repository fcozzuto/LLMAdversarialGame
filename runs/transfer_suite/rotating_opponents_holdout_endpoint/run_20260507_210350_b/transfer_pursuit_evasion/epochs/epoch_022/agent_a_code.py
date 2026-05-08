def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit", "attacker"))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", None)
    target = (ox, oy)
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                best = (int(rx), int(ry))
        if best is not None:
            target = best

    best_score = -10**18 if pursuer else 10**18
    best_move = (0, 0)
    tx, ty = target
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        if pursuer:
            score = -d_to_target * 3 - d_to_opp
        else:
            score = d_to_target * 3 + d_to_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]