def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_corner_drift():
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    if not resources:
        return best_corner_drift()

    # Pick a move that maximizes expected lead over opponent for the best target.
    # Tie-break: smaller distance to nearest resource, and prefer staying legal with no obstacle penalty.
    best_move, best_val = [0, 0], -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        # evaluate best target from our next position
        move_val = -10**18
        nearest_ours = 10**9
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            nearest_ours = d_our if d_our < nearest_ours else nearest_ours

            # Reward being strictly closer; penalize being not-closer.
            lead = d_opp - d_our  # positive means we arrive sooner (or same is neutral)
            # Stronger emphasis on winning races, weaker on general closeness.
            v = 8.0 * lead - 1.0 * d_our
            if v > move_val:
                move_val = v

        # mild preference to reduce distance to any resource and avoid getting stuck
        # (prevents edge cases where multiple targets yield similar race scores)
        extra = -0.25 * nearest_ours
        # obstacle proximity penalty from our next cell neighbors (discourage dead-ends)
        adj_pen = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < gw and 0 <= ay < gh and (ax, ay) in obstacles:
                adj_pen += 1
        move_val += extra - 0.08 * adj_pen

        if move_val > best_val:
            best_val = move_val
            best_move = [dxm, dym]

    return best_move