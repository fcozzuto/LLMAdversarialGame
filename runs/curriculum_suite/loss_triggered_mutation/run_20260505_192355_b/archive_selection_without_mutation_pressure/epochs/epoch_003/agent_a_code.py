def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        best = min(legal, key=lambda d: abs((sx + d[0]) - ox) + abs((sy + d[1]) - oy))
        return [best[0], best[1]]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_target = None
    best_gain = -10**9
    for tx, ty in resources:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        gain = opd - myd
        if gain > best_gain or (gain == best_gain and (myd < dist(sx, sy, best_target[0], best_target[1]) if best_target else True)):
            best_gain = gain
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = None
    best_d = 10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
        elif d == best_d and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]