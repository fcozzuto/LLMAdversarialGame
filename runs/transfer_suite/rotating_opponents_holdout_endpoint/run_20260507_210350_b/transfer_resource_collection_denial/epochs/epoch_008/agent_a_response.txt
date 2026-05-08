def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_r = None
    best_key = None

    # Score resources by: how much closer we are than opponent, but also bias to earlier pickup.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: we can arrive not much later than opponent; within that, maximize (do-ds), then minimize ds.
        can_race = 1 if ds <= do + 1 else 0
        key = (-(can_race), (ds - do), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best_r

    # When opponent is very close to our target, shift to the nearest alternate resource to reduce denial by timing.
    if resources and cheb(ox, oy, tx, ty) <= 1:
        alt = None
        alt_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (0 if ds <= do + 1 else 1, ds - do, ds, rx, ry)
            if alt_key is None or key < alt_key:
                alt_key = key
                alt = (rx, ry)
        if alt is not None:
            tx, ty = alt

    # Greedy step toward (tx,ty), but avoid moving into obstacles; tie-break with distance to opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: keep away from opponent to avoid steal/contest.
        score = (d_to_target, -d_to_opp, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]