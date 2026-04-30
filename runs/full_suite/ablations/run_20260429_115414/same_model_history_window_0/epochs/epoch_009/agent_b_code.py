def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_dist(x, y):
        if not resources:
            return None
        best = 10**9
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dres = nearest_dist(nx, ny)
        dopt = abs(nx - ox) + abs(ny - oy)
        if dres is None:
            score = dopt
        else:
            score = -dres + 0.01 * dopt
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]