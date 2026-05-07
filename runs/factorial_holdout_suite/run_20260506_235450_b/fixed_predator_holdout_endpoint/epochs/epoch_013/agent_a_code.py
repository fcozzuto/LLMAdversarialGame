def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate each next cell with a simple contest heuristic against a denier.
    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = -0.01 * md(nx, ny, ox, oy)  # slightly keep distance from denier
        # Choose the best resource to pursue from this next position.
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # If we are earlier or equal, reward heavily (resource is likely ours).
            # If later, penalize strongly (denier likely grabs it).
            if sd <= od:
                gain = 12.0 / (1 + sd)
                # Extra bias: if we can get it "soon", even better.
                gain += 1.5 / (1 + max(0, od - sd))
                # Mild preference to reduce remaining self distance.
                gain += 0.05 * (od - sd)
            else:
                # Penalize being behind; stronger if opponent is much closer.
                gain = -(10.0 + 3.0 * (od - sd)) / (1 + sd)
                # Small extra penalty if by moving here we also approach the denier's likely target closely.
                gain -= 0.2 * (od - sd) / (1 + od)
            val = max(val, val + gain)  # deterministic: accumulate by best-over-resources using max trick
        # The above 'max trick' is unconventional; replace with direct best resource value:
        # (kept deterministic by re-evaluating correctly)
        best_res_val = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if sd <= od:
                res_val = 12.0 / (1 + sd) + 1.5 / (1 + max(0, od - sd)) + 0.05 * (od - sd)
            else:
                res_val = -(10.0 + 3.0 * (od - sd)) / (1 + sd) - 0.2 * (od - sd) / (1 + od)
            if res_val > best_res_val:
                best_res_val = res_val
        # Add a tiny preference for moving toward the overall nearest resource when contested.
        nearest = min(resources, key=lambda p: md(nx, ny, p[0], p[1]))
        cont_bias = -0.02 * md(nx, ny, nearest[0], nearest[1])
        val = best_res_val + cont_bias
        # Deterministic tie-break: lexicographic favor earlier moves in list order.
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move