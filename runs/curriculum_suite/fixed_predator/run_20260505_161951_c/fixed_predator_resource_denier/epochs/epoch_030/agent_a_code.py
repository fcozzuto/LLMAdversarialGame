def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # drift away from opponent while expanding territory
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) - 0.01 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            # deterministic tie-break: prefer smallest (dx,dy) in dirs order
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose a target resource that we can reach earlier than the opponent.
    # Then choose the step that maximizes the same advantage for the resulting position.
    best_step = (0, 0)
    best_step_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # small penalty for moving toward obstacles adjacency (deterministic local avoidance)
        adj_pen = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                adj_pen += 1

        # evaluate best resource under this step
        step_best = -10**18
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # primary: advantage in reaching resource; secondary: get closer; tertiary: centrality
            adv = (opp_d - self_d) * 1000
            clos = -self_d * 2
            center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.001
            # discourage picking resources that are already "claimed" by being too close to opponent
            deny_bias = 0 if opp_d >= self_d else (opp_d - self_d) * 50
            v = adv + clos + center + deny_bias - adj_pen * 0.5
            if v > step_best:
                step_best = v

        if step_best > best_step_val:
            best_step_val = step_best
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]