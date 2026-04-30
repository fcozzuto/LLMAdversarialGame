def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target resource: prefer ones where we are closer than opponent, then closest overall.
    best = None  # (priority, dself, dopp, tx, ty)
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        dself = dist2((sx, sy), (rx, ry))
        dopp = dist2((ox, oy), (rx, ry))
        closer = 0 if dself <= dopp else 1  # 0 is better
        cand = (closer, dself, dopp, rx, ry)
        if best is None or cand < best:
            best = cand
    if best is not None:
        tx, ty = best[3], best[4]
    else:
        # No resources: move away from opponent if close, else toward center.
        tx, ty = (w // 2), (h // 2)

    # Pick move that minimizes distance to target, avoids obstacles, and discourages stepping toward opponent if contested.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = dist2((nx, ny), (tx, ty))
        d_to_opp = dist2((nx, ny), (ox, oy))
        # If a resource exists, lightly avoid giving the opponent an edge near them; otherwise just maximize separation.
        opp_term = d_to_opp if best is None or (best[0] == 1) else -d_to_opp * 0.25
        score = d_to_target + opp_term
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If every move was blocked, fall back to staying still (engine will keep in place).
    return [int(best_move[0]), int(best_move[1])]