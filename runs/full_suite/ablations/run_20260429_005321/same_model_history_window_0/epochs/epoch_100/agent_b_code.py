def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]

    # Pick a target resource: prefer ones where we're much closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        key = (d_opp - d_self, -d_self, -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cur_d = cheb(sx, sy, tx, ty)
    best_moves = []
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # primary: reduce distance; secondary: also consider moving away from opponent slightly
        opp_d = cheb(ox, oy, nx, ny)
        score = (-d, (opp_d), -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_moves = [[dx, dy]]
        elif score == best_score:
            best_moves.append([dx, dy])

    if best_moves:
        return best_moves[0]
    return [0, 0]