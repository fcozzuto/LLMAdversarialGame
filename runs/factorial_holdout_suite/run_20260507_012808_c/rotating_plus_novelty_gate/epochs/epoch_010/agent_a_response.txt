def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)

        # Prefer diagonal if it helps (otherwise axial).
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        # If blocked, try other legal deltas.
        all_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        seen = set()
        for m in cand + all_moves:
            if m in seen:
                continue
            seen.add(m)
            nx, ny = sx + m[0], sy + m[1]
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            return [m[0], m[1]]
        return [0, 0]

    # Race/deny: target a resource where opponent is at least as close as we are.
    best = None  # (score, rx, ry)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we can't win the race, still deny the most immediately reachable by opponent.
        # Negative ds helps us; positive (do-ds) punishes losing races.
        # Add slight bias toward closer resources for collecting.
        score = (do - ds) * 10 - ds
        # Ensure we strongly focus on "opponent is close" targets
        if do <= ds:
            score -= 100
        if best is None or score < best[0] or (score == best[0] and (rx, ry) < (best[1], best[2])):
            best = (score, rx, ry)

    _, tx, ty = best
    # If we are already at the target, move toward next denied resource by flipping strategy:
    if (sx, sy) == (tx, ty):
        # Choose a different resource deterministically: nearest to opponent (deny).
        best2 = None
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            d = cheb(ox, oy, rx, ry)
            ds = cheb(sx, sy, rx, ry)
            score = d * 10 + ds
            if best2 is None or score < best2[0] or (score == best2[0] and (rx, ry) < (best2[1], best2[2])):
                best2 = (score, rx, ry)
        if best2 is None:
            return [0, 0]
        _, tx, ty = best2[0], best2[1], best2[2]

    # Small anti-chase: if moving directly would step into adjacency allowing immediate opponent capture,
    # adjust by choosing a best step toward a neighboring resource if it exists.
    step = best_step(tx, ty)
    nx, ny = sx + step[0], sy + step[1]
    if (nx, ny) == (ox, oy):
        return [0, 0]

    return step