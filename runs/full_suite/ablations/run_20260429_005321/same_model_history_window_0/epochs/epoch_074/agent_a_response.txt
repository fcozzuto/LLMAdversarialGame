def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, 0, w-1), clamp(sy + dy, 0, h-1)
            if (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Prefer resources where we are advancing more than the opponent, and avoid obstacles.
    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w-1), clamp(sy + dy, 0, h-1)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Score: maximize our advantage to the best resource from the candidate state.
        candv = -10**18
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)

            # Encourage reaching quickly (small myd), while being far from opponent (large opd)
            # and slightly discourage moving away from current position.
            step_back_pen = 0
            if myd > dist2(sx, sy, rx, ry):
                step_back_pen = 3

            v = (opd - myd) - 0.05 * myd + 0.01 * (sx + sy - nx - ny) - step_back_pen
            if v > candv:
                candv = v

        # Tie-break: if equal, prefer moves that reduce distance to nearest resource.
        if candv > bestv:
            bestv = candv
            best = (dx, dy)
        elif candv == bestv:
            cur_near = min(dist2(sx, sy, rx, ry) for rx, ry in resources)
            new_near = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
            cur_best_near = min(dist2(sx + best[0], sy + best[1], rx, ry) for rx, ry in resources)
            if new_near < cur_best_near:
                best = (dx, dy)

    return [best[0], best[1]]