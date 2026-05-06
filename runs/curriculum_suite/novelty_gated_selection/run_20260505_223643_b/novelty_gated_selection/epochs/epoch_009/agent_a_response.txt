def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target that's favorable by distance advantage; if no clear advantage, pick a "swing" target far from opponent.
    best = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive means we are closer
        # Encourage breaking symmetry with a quadrant bias (deterministic).
        quad_bias = 0
        if (rx + ry) % 2 == 0:
            quad_bias = 0.15
        # Favor targets that are hard for opponent: large do and our manageable ds.
        swing = (advantage + 0.35) + 0.02 * (do - ds) + quad_bias
        # If we are already closer, make it strongly preferred.
        val = swing + (8.0 if advantage > 0 else 0.0) + (3.0 if advantage > 1 else 0.0)
        if best is None or val > best[0]:
            best = (val, rx, ry, ds, do)
    _, tx, ty, _, _ = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        d_opp_to_target = cheb(ox, oy, tx, ty)
        # Make progress to target while trying to keep the opponent from getting meaningfully closer.
        my_score = -d_to_target + 0.06 * d_to_opp
        # If opponent is close to the target, we prefer moves that increase their relative disadvantage.
        my_score += 0.5 if cheb(nx, ny, tx, ty) < d_opp_to_target else 0.0
        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically.
        if my_score > best_s or (my_score == best_s and (dx, dy) < best_m):
            best_s = my_score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]