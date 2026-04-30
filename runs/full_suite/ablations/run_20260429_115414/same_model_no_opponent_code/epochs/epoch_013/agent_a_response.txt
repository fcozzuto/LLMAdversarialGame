def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        resources = [[w - 1, h - 1]]
    resources = [(int(x), int(y)) for x, y in resources if free(int(x), int(y))] or [(w - 1, h - 1)]

    # Pick resource: strongly prefer reducing opponent advantage, then closeness, then resource preference.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key: (opponent advantage, closer-to-self, farther-from-opponent, closer-by-fine tie, position)
        key = (od - sd, -sd, od, - (rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # If opponent is extremely close to our target, bias to block by steering towards an intermediate point.
    opp_to_target = cheb(ox, oy, tx, ty)
    bias_block = (opp_to_target <= 2)

    # One-step evaluation.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Intermediate point: move towards target but also nudge away from opponent if blocking.
    if bias_block:
        # step direction from opponent to target; choose a point one step closer to target along that direction
        stepx = 0 if ox == tx else (1 if tx > ox else -1)
        stepy = 0 if oy == ty else (1 if ty > oy else -1)
        ix, iy = tx - stepx, ty - stepy  # roughly "before" target from opponent perspective
        if not free(ix, iy):
            ix, iy = tx, ty
        block_point = (ix, iy)
    else:
        block_point = (tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_b = cheb(nx, ny, block_point[0], block_point[1])
        d_opp = cheb(nx, ny, ox, oy)

        # Prefer smaller distance to block point / target, avoid giving opponent huge lead,
        # and keep distance from opponent when not directly improving.
        # Also slightly prefer staying on-grid and deterministic tie-break by move order.
        opp_lead = cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)
        score = (-(0.6 * d_to_b + 0.4 * d_to_t),  # primary: approach
                 d_opp,                             # secondary: keep away
                 -opp_lead)                         # tertiary: reduce opponent lead

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]