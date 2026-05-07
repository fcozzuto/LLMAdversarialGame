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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 3 if sx > (gw - 1) // 2 else (4 if sx < (gw - 1) // 2 else sx)
        ty = 3 if sy > (gh - 1) // 2 else (4 if sy < (gh - 1) // 2 else sy)
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_resource = None
    best_score = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer resources where we are sooner; then prefer closer overall.
        score = (d_opp - d_me) * 100 - d_me
        if score > best_score:
            best_score = score
            best_resource = (rx, ry)

    rx, ry = best_resource
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # If tie, also try to worsen opponent's best rush slightly via their nearest resource.
        opp_pressure = 0
        if resources:
            # Deterministic: approximate opponent target as resource with minimal cheb from opponent.
            best_opp = None
            best_opp_d = 10**9
            for px, py in resources:
                d = cheb(ox, oy, px, py)
                if d < best_opp_d:
                    best_opp_d = d
                    best_opp = (px, py)
            opp_pressure = cheb(nx, ny, best_opp[0], best_opp[1]) if best_opp else 0
        v = (opp_d - my_d) * 100 - my_d + 0.01 * opp_pressure
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move