def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obs_set = {(p[0], p[1]) for p in obstacles}
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_resource_from(pos):
        best_r = resources[0]
        best_val = -10**9
        for r in resources:
            v = dist(pos, (r[0], r[1]))
            vo = dist((ox, oy), (r[0], r[1]))
            # Prefer resources we are closer to (opp_dist - self_dist bigger)
            val = (vo - v) * 2 - v * 0.2
            if val > best_val:
                best_val, best_r = val, r
        return (best_r[0], best_r[1])

    target = best_resource_from((x, y))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        self_d = dist((nx, ny), target)
        opp_d = dist((ox, oy), target)
        # Move toward target, but don't let opponent gain lead; also slightly central bias.
        lead = (opp_d - self_d)
        center_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))
        score = lead * 5 - self_d + center_bias
        # If the target is blocked from immediate approach, add mild preference for improving lead on any resource.
        if self_d <= 1:
            pass
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        # Fallback: take any move that improves lead to the chosen target
        tx, ty = target
        options = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                lead = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
                options.append(((lead, -dist((nx, ny), (tx, ty))), (dx, dy)))
        if options:
            options.sort(reverse=True)
            return [options[0][1][0], options[0][1][1]]
    return [best_move[0], best_move[1]]