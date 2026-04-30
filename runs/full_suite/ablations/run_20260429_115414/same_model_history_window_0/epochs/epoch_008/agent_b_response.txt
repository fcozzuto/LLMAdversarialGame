def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Pick resource where we are relatively closer than opponent (lower is better)
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; use tie-breakers for determinism
        key = (ds - do, ds, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Move that reduces our distance to target; slight preference to avoid moving into opponent distance decrease
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Higher d_opp is safer (reduce opponent contest), so use -d_opp
        mkey = (d_self, -d_opp, abs(dx) + abs(dy), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # If all moves blocked, stay
    if best_mkey is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]