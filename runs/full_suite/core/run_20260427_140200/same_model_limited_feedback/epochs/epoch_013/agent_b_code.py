def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Pick best target resource: prefer ones we reach sooner (chebyshev distance with diagonal moves)
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # deterministic tie-break: favor lower resource coords if equal
        key = (d_me - 2 * d_opp, d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Choose a legal move that reduces distance to chosen target; break ties by also considering opponent pressure
    best_mv = (0, 0)
    best_mv_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_after = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(nx, ny, ox, oy)
        # primary: closer to target; secondary: farther from opponent (safer contest); tertiary: lexicographic move
        key = (d_after, -d_opp_after, dx, dy)
        if best_mv_key is None or key < best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    # If all moves blocked (rare), stay
    return [int(best_mv[0]), int(best_mv[1])]