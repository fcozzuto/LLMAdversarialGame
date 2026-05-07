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
        # deterministic "seek center then slight toward opponent's side"
        tx = gw // 2
        ty = gh // 2
        if sx < tx: tx = max(0, tx - 1)
        if sy < ty: ty = max(0, ty - 1)
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

    # Evaluate each possible next move by the best resource we could aim to secure
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        me_d = cheb(nx, ny, ox, oy)  # not used directly, but stable
        # choose resource that maximizes lead gain: (opp_dist - self_dist)
        best_res_gain = -10**18
        best_res_self = 10**9
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            gain = d_op - d_me
            if gain > best_res_gain or (gain == best_res_gain and (d_me < best_res_self or (d_me == best_res_self and (rx, ry) < (best_res_self, best_res_self)))):
                best_res_gain = gain
                best_res_self = d_me

        # strong preference: move that gets us closer than opponent to some resource, and secondarily shorter path
        # tiny tie-break toward staying away from obstacles is implicit via legality
        v = best_res_gain * 1000 - best_res_self
        # slight bias to approach any currently advantageous point
        if (nx, ny) in [(rx, ry) for rx, ry in resources]:
            v += 5000
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move