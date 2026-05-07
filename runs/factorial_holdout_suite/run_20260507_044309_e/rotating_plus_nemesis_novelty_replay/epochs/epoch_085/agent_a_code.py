def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not res:
        return [0, 0]

    # Pick target by "race advantage": larger means we are closer than opponent
    best = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, sd, od)
    _, tx, ty, self_d, opp_d = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If opponent is closer or equal, prioritize "denial" near that resource (move that makes it hardest for opponent next),
    # otherwise prioritize our distance reduction to the target.
    want_denial = opp_d <= self_d

    best_move = None
    for dx, dy, nx, ny in moves:
        if want_denial:
            # Hypothetical: estimate how much we push ourselves away from opponent reach to target,
            # while still moving somewhat toward target to potentially secure it.
            my_to = man(nx, ny, tx, ty)
            opp_to = man(ox, oy, tx, ty)
            # Use "denial score": increase the distance from opponent to (our next) along line to target proxy
            # via chebyshev between opponent and our next; deterministic and cheap.
            cx = nx - ox
            if cx < 0: cx = -cx
            cy = ny - oy
            if cy < 0: cy = -cy
            opp_proxy = cx if cx > cy else cy
            score = (opp_proxy, -my_to)
        else:
            my_to = man(nx, ny, tx, ty)
            score = (-my_to, nx, ny)
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]