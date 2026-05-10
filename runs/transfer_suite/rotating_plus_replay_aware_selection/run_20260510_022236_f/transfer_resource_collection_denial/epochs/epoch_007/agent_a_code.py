def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_set = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_x(x):
        return x if 0 <= x < w else (0 if x < 0 else w - 1)

    def clamp_y(y):
        return y if 0 <= y < h else (0 if y < 0 else h - 1)

    # Pick a target that is either immediately mine (I can arrive no later),
    # or the most urgent contested one where I am relatively closest to arriving.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Priority order:
        # 1) Resources I can reach no later than opponent
        # 2) Otherwise, contest the resource with smallest (myd-opd) then smallest myd
        if myd <= opd:
            key = (0, myd, rx * 64 + ry)
        else:
            key = (1, myd - opd, myd, -(rx * 64 + ry))
        if best_key is None or key < best_key:
            best_key = key
            best_r = [rx, ry]

    tx, ty = best_r[0], best_r[1]
    if sx == tx and sy == ty:
        # Already on a resource; deterministically move to a nearby alternative.
        best2 = None
        best_key2 = None
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd <= opd:
                key = (0, myd, rx * 64 + ry)
            else:
                key = (1, myd - opd, myd, -(rx * 64 + ry))
            if best_key2 is None or key < best_key2:
                best_key2 = key
                best2 = [rx, ry]
        if best2 is None:
            return [0, 0]
        tx, ty = best2[0], best2[1]

    # Greedy local step toward target with obstacle avoidance
    dx_opts = (-1, 0, 1)
    dy_opts = (-1, 0, 1)
    candidates = []
    for dx in dx_opts:
        for dy in dy_opts:
            nx = clamp_x(sx + dx)
            ny = clamp_y(sy + dy)
            if (nx, ny) in obs_set:
                continue
            dist = cheb(nx, ny, tx, ty)
            # Tie-break: prefer progress in both axes toward target, then deterministic order.
            prog = (abs(tx - sx) - abs(tx - nx)) + (abs(ty - sy) - abs(ty - ny))
            candidates.append((dist, -prog, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]