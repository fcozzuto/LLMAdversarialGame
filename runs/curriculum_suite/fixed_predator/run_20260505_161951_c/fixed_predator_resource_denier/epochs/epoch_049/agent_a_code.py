def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_value(nx, ny):
        if resources:
            best = -10**18
            best_neg = -10**18
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                rel = op_d - my_d
                # Prefer resources where we are ahead; otherwise still try to contest the most dangerous ones.
                if rel >= 0:
                    v = 600 * rel - 3 * my_d
                    if v > best:
                        best = v
                else:
                    v = 450 * rel + 4 * op_d - 2 * my_d
                    if v > best_neg:
                        best_neg = v
            v = best if best > -10**17 else best_neg
        else:
            # No visible resources: head to far corner while keeping distance from opponent.
            tx, ty = (w - 1, h - 1) if (x + y) <= (ox + oy) else (0, 0)
            v = 800 * cheb(nx, ny, ox, oy) - (abs(nx - tx) + abs(ny - ty))
        # Mild obstacle/edge penalty to reduce getting stuck near obstacles.
        v -= 5 * (not (0 < nx < w - 1 and 0 < ny < h - 1))
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            mx, my = nx + ax, ny + ay
            if not (0 <= mx < w and 0 <= my < h) or (mx, my) in obs:
                v -= 1
        return v

    best_move = (0, 0)
    best_v = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        v = step_value(nx, ny)
        if v > best_v or (v == best_v and (dx, dy) < best_move):
            best_v = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]