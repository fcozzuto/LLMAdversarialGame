def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    if resources:
        # Choose a target resource biased by who is closer.
        best = None
        best_val = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources we can reach first; otherwise still progress toward nearest.
            val = (do - ds) * 2.0 - ds * 0.5
            if best_val is None or val > best_val or (val == best_val and (tx, ty) < best):
                best_val = val
                best = (tx, ty)
        tx, ty = best
    else:
        # No resources: head to a corner away from opponent.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: cheb(ox, oy, p[0], p[1]) - cheb(sx, sy, p[0], p[1]))

    res_set = set((x, y) for x, y in resources)
    cur_dop = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_target = cheb(nx, ny, tx, ty)
        score = -d_to_target

        # If we step onto a resource, strongly prefer it.
        if (nx, ny) in res_set:
            score += 1000

        # Keep distance from opponent slightly (avoid giving easy steal).
        dop = cheb(nx, ny, ox, oy)
        score += (dop - cur_dop) * 0.15

        # Small deterministic bias toward center to avoid oscillation when tied.
        score += -0.001 * cheb(nx, ny, (w - 1) / 2, (h - 1) / 2)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        return [0, 0]
    return [dx, dy]