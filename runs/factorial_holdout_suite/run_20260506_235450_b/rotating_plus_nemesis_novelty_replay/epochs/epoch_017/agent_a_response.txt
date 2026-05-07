def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = dist2(nx, ny, tx, ty) + dist2(nx, ny, ox, oy) * 0.001
            if best is None or k < best:
                best = k
                bestm = [mx, my]
        return bestm if best is not None else [0, 0]

    best_score = None
    best_move = [0, 0]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate best achievable target for us from this move, while heavily penalizing "denied" targets.
        best_for_me = None
        for rx, ry in resources:
            d_me = dist2(nx, ny, rx, ry)
            d_op = dist2(ox, oy, rx, ry)
            # If opponent is closer, this target is risky; penalize more strongly to prefer deniable routes.
            risk = 0
            if d_op + 1 < d_me:
                risk = (d_me - d_op) * 5 + 50
            # Prefer targets that are both near and far from opponent.
            value = -d_me - risk + dist2(nx, ny, ox, oy) * 0.01
            if best_for_me is None or value > best_for_me:
                best_for_me = value

        # Also discourage moves that let opponent be simultaneously much closer to any resource.
        opp_best = None
        for rx, ry in resources:
            opp_best_val = -dist2(ox, oy, rx, ry)
            if opp_best is None or opp_best_val > opp_best:
                opp_best = opp_best_val

        score = best_for_me
        if best_score is None or score > best_score or (score == best_score and [mx, my] < best_move):
            best_score = score
            best_move = [mx, my]

    return best_move if best_move is not None else [0, 0]