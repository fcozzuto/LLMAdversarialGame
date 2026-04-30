def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = 10**18

    # Identify key resources: closest to us and closest to opponent.
    my_best = min(resources, key=lambda r: king_dist(sx, sy, r[0], r[1]))
    op_best = min(resources, key=lambda r: king_dist(ox, oy, r[0], r[1]))
    # Also pick the "contested" resource that opponent is currently closer to than us.
    contested = None
    cont_score = -10**18
    for rx, ry in resources:
        dm = king_dist(sx, sy, rx, ry)
        do = king_dist(ox, oy, rx, ry)
        if do < dm:
            # Higher means more urgent for us to contest.
            urgency = (dm - do) - 0.1 * (dm + do) + (rx * 0 + 1)  # deterministic tie-bias
            if urgency > cont_score:
                cont_score = urgency
                contested = (rx, ry)

    target = contested if contested is not None else (my_best[0], my_best[1])

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        # Primary: minimize our distance to target (contest or best).
        d_self = king_dist(nx, ny, target[0], target[1])

        # Secondary: reduce opponent's progress to their best.
        d_op = king_dist(nx, ny, op_best[0], op_best[1])
        # Interference proxy: if we move closer to where opponent is aiming, we can block/arrive near it.
        op_progress = king_dist(ox, oy, op_best[0], op_best[1]) - king_dist(nx, ny, op_best[0], op_best[1])

        # Reward stepping onto a resource.
        hit = 1 if (nx, ny) in set(resources) else 0

        # If we're already closer than opponent to target after move, prefer it strongly.
        do_to_target = king_dist(ox, oy, target[0], target[1])
        tighter = (do_to_target - d_self)

        val = (10 * d_self) - (3.5 * hit) - (2.0 * tighter) + (1.2 * d_op) - (1.5 * op_progress) + (0.6 * obs_pen(nx, ny))
        if val < best_val:
            best_val = val
            best_move = [mx, my]

    return best_move