def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

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
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        v_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer arriving earlier; then prefer shorter self distance.
            v = (d_opp - d_me) * 20 - d_me
            # Tiny secondary bias toward nearer resources overall.
            v -= 0.01 * (abs(nx - sx) + abs(ny - sy))
            if v > v_best:
                v_best = v
        # Prefer moves that secure the best target, also slight penalty for moving.
        v_final = v_best - 0.001 * (abs(dxm) + abs(dym))
        if v_final > best_val:
            best_val = v_final
            best_move = [dxm, dym]
    return best_move