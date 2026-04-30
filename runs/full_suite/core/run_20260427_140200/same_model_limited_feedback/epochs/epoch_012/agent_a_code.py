def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    deltas = [[dx, dy] for dx in dxs for dy in dys]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource that we can reach relatively better than the opponent.
    best_r = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds)  # higher means we are closer than opponent
        # small tie-break to prefer nearer to us and to center
        val = val * 1000 - ds * 3 - (abs(rx - w // 2) + abs(ry - h // 2))
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)

    # If no resources listed, drift toward opponent but keep away from obstacles.
    if best_r is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    # Evaluate moves.
    best_m = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_new = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target; avoid allowing opponent to get much closer simultaneously.
        opp_to_target = cheb(ox, oy, tx, ty)
        # encourage moves that reduce our distance more than their distance changes
        score = -ds_new * 10 + do_new * 1.2
        score += (opp_to_target - ds_new) * 2.0
        # obstacle proximity penalty
        if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles or (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
            score -= 0.8
        # deterministic tie-break: fixed order deltas already provides stable first-max
        if best_score is None or score > best_score:
            best_score = score
            best_m = [dx, dy]

    return best_m