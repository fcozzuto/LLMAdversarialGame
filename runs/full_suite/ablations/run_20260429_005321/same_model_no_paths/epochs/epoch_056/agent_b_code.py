def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner than opponent (more negative is better),
        # then prefer closer to us, then deterministic by coordinates.
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_after = None
    best_improve = None

    # Prefer moves that reduce distance to chosen target; if tie, reduce opponent advantage;
    # then deterministic by delta order.
    delta_order = {d: i for i, d in enumerate(deltas)}
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ad = cheb(nx, ny, tx, ty)
        improve = cur_d - ad
        # Opponent advantage proxy: lower (our_dist - opp_dist) better.
        my_adv = ad - cheb(ox, oy, tx, ty)
        after = (-(improve), my_adv, ad, delta_order[(dx, dy)])
        if best_after is None or after < best_after:
            best_after = after
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]