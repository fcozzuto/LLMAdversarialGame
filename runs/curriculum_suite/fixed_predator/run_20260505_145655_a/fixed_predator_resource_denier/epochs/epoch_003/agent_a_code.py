def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs_set:
                nx, ny = sx, sy
            d = dist2((nx, ny), (tx, ty))
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    us = (sx, sy)
    op = (ox, oy)
    my_target = min(resources, key=lambda r: dist2(us, r))
    opp_target = min(resources, key=lambda r: dist2(op, r))

    # Prefer: get closer to my_target; also move so opponent is less likely to reach opp_target.
    # Deterministic tie-breaker: lexicographic on (dx, dy) via ordered moves list.
    best = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            nx, ny = sx, sy
        ns = (nx, ny)

        d_my = dist2(ns, my_target)
        d_op_to_opp = dist2(op, opp_target)
        d_op_after = dist2((clamp(ox + (1 if opp_target[0] > ox else -1 if opp_target[0] < ox else 0), 0, w - 1),
                             clamp(oy + (1 if opp_target[1] > oy else -1 if opp_target[1] < oy else 0), 0, h - 1)), opp_target)

        # Opponent likely moves toward opp_target; we hedge by increasing our distance to opp_target
        # and decreasing our distance to my_target.
        hedge = dist2(ns, opp_target) - d_op_to_opp

        # If we can land on my_target, go directly.
        on_my = 1 if ns == tuple(my_target) else 0
        # If we also block (adjacent) to opp_target, slight bonus.
        block = 1 if dist2(ns, opp_target) <= 2 else 0

        # Lower is better overall.
        score = (0 if on_my else 1) * 10000 + d_my - 0.35 * hedge - 0.25 * block - 0.05 * (d_op_after - d_op_to_opp)

        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]