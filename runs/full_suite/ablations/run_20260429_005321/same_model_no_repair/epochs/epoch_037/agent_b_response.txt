def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    cx = (gw - 1) / 2.0
    cy = (gh - 1) / 2.0

    best = None
    best_score = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        center = -0.001 * ((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        # Encourage taking a lead, discourage long trips, slight preference for nearer resources.
        score = lead * 1000 - ds * 2 + center
        if score > best_score or (score == best_score and (rx, ry) < (best[0], best[1])):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    rx, ry = best

    # If we are already blocked by target being an obstacle, just do nothing.
    # (Resources should not be obstacles, but keep it safe.)
    if (rx, ry) in obs:
        return [0, 0]

    cur_ds = man(sx, sy, rx, ry)

    # Evaluate candidate moves: prefer reducing our distance to target, keep obstacles out,
    # and also keep making lead vs opponent at the target.
    cur_do_target = man(ox, oy, rx, ry)
    best_move = (0, 0)
    best_move_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nds = man(nx, ny, rx, ry)
        # Opponent lead at the target doesn't change this turn, but we still scale by nds.
        step_bias = -0.001 * (dx * dx + dy * dy)  # slight preference to smaller steps
        # Big reward for taking the distance down; smaller reward for not increasing.
        move_score = (cur_ds - nds) * 50 - nds * 1.5 + step_bias
        # Deterministic tie-breaker: lower (dx,dy) tuple wins if equal.
        if move_score > best_move_score or (move_score == best_move_score and (dx, dy) < best_move):
            best_move_score = move_score
            best_move = (dx, dy)

    if best_move_score == -10**18:
        return [0, 0]
    return [best_move[0], best_move[1]]