def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obst
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def greedy_step(ax, ay, tx, ty):
        best = None
        bestd = 10**9
        # deterministic tie-break: prefer smaller (mdx,mdy) by iteration order
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        return best if best is not None else (ax, ay)

    if not resources:
        return [0, 0]

    # Simulate a short greedy race for each resource; opponent also greedily chases same target.
    horizon = 6
    best_target = None
    best_tuple = None  # (we_time, -lead, my_time, rx, ry)
    for rx, ry in resources:
        ax, ay = sx, sy
        bx, by = ox, oy
        we_t = None
        opp_t = None
        for t in range(horizon + 1):
            if we_t is None and (ax == rx and ay == ry):
                we_t = t
            if opp_t is None and (bx == rx and by == ry):
                opp_t = t
            if we_t is not None and opp_t is not None:
                break
            if t < horizon:
                if we_t is None:
                    ax, ay = greedy_step(ax, ay, rx, ry)
                if opp_t is None:
                    bx, by = greedy_step(bx, by, rx, ry)

        if we_t is None: we_t = horizon + 1
        if opp_t is None: opp_t = horizon + 1

        lead = (opp_t - we_t)  # positive means we arrive earlier
        tup = (we_t, -lead, we_t, rx, ry)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_target = (rx, ry)

    rx, ry = best_target
    nx, ny = greedy_step(sx, sy, rx, ry)
    dx, dy = nx - sx, ny - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]