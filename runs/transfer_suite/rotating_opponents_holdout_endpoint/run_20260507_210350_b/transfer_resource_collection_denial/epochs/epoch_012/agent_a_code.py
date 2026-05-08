def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"] if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick best resource to aim for, preferring ones we are earlier than opponent for.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # If opponent can reach sooner, heavily penalize. Add tiny bias to vary from opponent.
        key = (ds - 1.8 * do, abs(tx - ox) + abs(ty - oy) * 0.01, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Choose immediate move that minimizes our distance to target, with tie-break: increase opponent distance.
    best_m = [0, 0]
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Also discourage stepping onto squares that are immediate opponent bait: maximize distance between agents.
        agent_sep = md(nx, ny, ox, oy)
        sc = (ds2, -agent_sep, do2, nx, ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_m = [dx, dy]

    return best_m