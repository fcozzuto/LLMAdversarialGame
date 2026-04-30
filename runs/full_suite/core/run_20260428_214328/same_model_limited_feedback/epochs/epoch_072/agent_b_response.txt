def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick resource where we are relatively closer than opponent
    tx, ty = None, None
    best = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, cheb(ox, oy, rx, ry))
            if best is None or key < best:
                best = key
                tx, ty = rx, ry
    if tx is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        tx = int(tx + 0.5) if tx >= 0 else int(tx - 0.5)
        ty = int(ty + 0.5) if ty >= 0 else int(ty - 0.5)

    cur_target_dist = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_dist = cur_target_dist
    best_block = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Primary: get closer to target. Secondary: avoid helping opponent (prefer moves that
        # do not reduce opponent's distance as much).
        opd = cheb(ox, oy, tx, ty)
        next_opd = opd
        if opd != 0:
            # Opponent is static this turn, so "blocking" is approximated by choosing moves that
            # reduce our distance significantly relative to how much they already have.
            pass
        key = (nd, nd - (opd - nd), abs(nx - tx) + abs(ny - ty))
        if nd < best_dist:
            best_dist = nd
            best_move = (dx, dy)
            best_block = key
        elif nd == best_dist:
            if best_block is None or key < best_block:
                best_move = (dx, dy)
                best_block = key

    return [best_move[0], best_move[1]]