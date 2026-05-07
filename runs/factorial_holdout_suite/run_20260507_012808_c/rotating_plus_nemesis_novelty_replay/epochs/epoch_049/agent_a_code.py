def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        # Prefer resources where we are not behind; if behind, pick the one closest to deny
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            behind = ds - do  # <=0 means we are earlier or tied
            # Tie-break: prefer smaller ds; add slight penalty if opponent is much closer
            score = (0 if behind <= 0 else 1000 + behind) + ds * 1.0
            # If opponent is closer, still allow picking to contest if very reachable
            if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[2]):
                best = (score, (rx, ry), (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: drift toward nearest corner that is not blocked
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            score = md(sx, sy, cx, cy) + 0.01 * md(ox, oy, cx, cy)
            if bestc is None or score < bestc[0]:
                bestc = (score, cx, cy)
        if bestc is None:
            return [0, 0]
        tx, ty = bestc[1], bestc[2]

    # Choose best immediate step that moves toward target and tries to avoid opponent proximity
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Heuristic: distance to target, then discourage stepping adjacent to opponent if target is contested
        dist_t = md(nx, ny, tx, ty)
        contested = 1 if resources and md(sx, sy, tx, ty) > md(ox, oy, tx, ty) else 0
        opp_dist = md(nx, ny, ox, oy)
        # If contested, maximize opp_dist; else just go toward target
        hscore = dist_t
        if contested:
            hscore = hscore * 10 + (-opp_dist)
        if hscore < best_move[0] or (hscore == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (hscore, dx, dy)

    return [int(best_move[1]), int(best_move[2])]