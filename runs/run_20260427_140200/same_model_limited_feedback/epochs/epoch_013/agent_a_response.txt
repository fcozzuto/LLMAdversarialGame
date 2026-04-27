def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    if not resources:
        return [0, 0]

    def clip(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) if (abs(dx) >= abs(dy)) else (dy if dy >= 0 else -dy)

    best_r = None
    best_s = -10**9
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        s = d_opp - d_self
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    tx, ty = best_r
    if best_s < 0:
        # Opponent likely closer: contest by moving to opponent's next step toward the closest resource.
        target = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
        rx, ry = target
        stepx = 0 if rx == ox else (1 if rx > ox else -1)
        stepy = 0 if ry == oy else (1 if ry > oy else -1)
        tx, ty = clip(ox + stepx, 0, w - 1), clip(oy + stepy, 0, h - 1)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = cheb(nx, ny, tx, ty)
        # Tie-break: slightly prefer moving away from being trapped near obstacles by using min distance to opponent
        if val < best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            oppd = cheb(nx, ny, ox, oy)
            curoppd = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if oppd > curoppd:
                best_move = (dx, dy)
    nx, ny = sx + best_move[0], sy + best_move[1]
    if (nx, ny) in obstacles:
        return [0, 0]
    return [best_move[0], best_move[1]]