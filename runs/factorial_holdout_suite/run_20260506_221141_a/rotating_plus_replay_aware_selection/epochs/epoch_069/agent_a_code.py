def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose the resource where we have the biggest speed advantage (ties resolved by our proximity)
        best_adv = -10**18
        best_self_d = 10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = (d_op - d_me)
            if adv > best_adv or (adv == best_adv and d_me < best_self_d):
                best_adv = adv
                best_self_d = d_me

        # Encourage collecting soon even if not fastest: higher (less negative) self distance helps earlier turns
        # Deterministic tie-break: prefer staying/earlier lex by move ordering already fixed.
        v = best_adv * 1000 - best_self_d
        if v > bestv:
            bestv = v
            best_move = [dx, dy]

    return best_move