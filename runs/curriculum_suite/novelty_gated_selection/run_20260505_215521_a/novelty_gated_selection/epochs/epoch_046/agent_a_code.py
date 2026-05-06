def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def best_resource_score(nx, ny):
        # Choose a resource where we are not too disadvantaged; otherwise pick best available.
        best = None
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            adv = opd - myd  # positive means we are closer
            # Penalty if opponent is likely to reach much sooner.
            val = myd - 2.5 * adv  # smaller better; makes disadvantage worse
            # Mild prefer currently closer to resources cluster by adding myd
            val += 0.15 * (myd * myd)
            if best is None or val < best[0]:
                best = (val, rx, ry, myd, opd)
        return best[1], best[2], best[3], best[4]

    best_move = (0, 0)
    best_val = None

    # Determine targeted resource from current position to stabilize path.
    tx, ty, _, _ = best_resource_score(sx, sy)

    # If opponent is extremely close, temporarily prioritize distance.
    close_op = (abs(sx - ox) + abs(sy - oy)) <= 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue

        # Objective components.
        myd = abs(nx - tx) + abs(ny - ty)
        d_op = abs(nx - ox) + abs(ny - oy)

        # If close, keep away more strongly.
        if close_op:
            val = myd * 1.2 - 3.5 * d_op
        else:
            # Also ensure we don't step into opponent's immediate grasp.
            val = myd - 1.7 * d_op

        # Resource-denial response: if opponent is closer to the current target, switch target value.
        # Evaluate best resource at this candidate to avoid being funneled.
        nTx, nTy, nMyD, nOpD = best_resource_score(nx, ny)
        if (nOpD - nMyD) > 1:
            # Opponent is likely to win that resource; discourage this move a bit.
            val += 6.0
        # Prefer reducing opponent's advantage overall.
        val += 0.15 * (nMyD - nOpD)

        # Deterministic tie-breaker: prefer moves with lexicographic (dx,dy) order as fallback.
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]