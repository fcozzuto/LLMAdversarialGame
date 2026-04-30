def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    target = None
    best = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        if d1 == 0:
            return [0, 0]
        score = d1 - 0.7 * d2  # prefer resources we can reach sooner
        if best is None or score < best:
            best = score
            target = (rx, ry)
    if target is None:
        return [0, 0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                opp_dist = cheb(nx, ny, ox, oy)
                # slight preference to approach target and avoid being too close to opponent
                moves.append((dist, -opp_dist, mx, my))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    # Prefer the direct reducing step if among best; otherwise take best deterministic
    best_move = [moves[0][2], moves[0][3]]
    direct = (dx, dy)
    for m in moves[:min(5, len(moves))]:
        if (m[2], m[3]) == direct:
            return [direct[0], direct[1]]
    return best_move