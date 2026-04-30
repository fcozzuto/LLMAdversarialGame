def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    cur_valid = [(dx, dy) for dx, dy in moves if valid(sx + dx, sy + dy)]
    if not cur_valid:
        return [0, 0]

    # Endgame: no resources left/none visible -> maximize distance from opponent
    if not resources or rem <= 0:
        best_key = None; best = [0, 0]
        for dx, dy in cur_valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            key = (d, -cheb(nx, ny, sx, sy), nx, ny)
            if best_key is None or key > best_key:
                best_key = key; best = [dx, dy]
        return best

    # Select a contested target: maximize (opp_dist - self_dist) with mild preference for nearer targets.
    opp_risk = []  # store (target, score_self_adv)
    for rx, ry in resources:
        d_s = cheb(sx, sy, rx, ry)
        d_o = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; also bias toward closer overall to reduce drift.
        key_score = (d_o - d_s, -(d_s + d_o), -rx, -ry)
        opp_risk.append(((rx, ry), key_score))
    opp_risk.sort(key=lambda t: t[1], reverse=True)
    target = opp_risk[0][0]
    tx, ty = target

    # Contest logic: if opponent is at most 1 step closer/equal than us, nudge toward the target.
    d_s0 = cheb(sx, sy, tx, ty)
    d_o0 = cheb(ox, oy, tx, ty)
    need_contest = (d_o0 <= d_s0)

    # Move choice: greedily maximize relative advantage after our move.
    best_key = None; best = [0, 0]
    for dx, dy in cur_valid:
        nx, ny = sx + dx, sy + dy
        d_s1 = cheb(nx, ny, tx, ty)
        # Relative advantage: how much we reduce opponent's effective lead by positioning.
        rel = (d_o0 - d_s1)
        # Mildly prefer improving distance to opponent as a tiebreak when contesting.
        d_opp1 = cheb(nx, ny, ox, oy)
        # Prefer blocking zones near the target: keep us close if opponent is near.
        dist_to_target = d_s1
        # Slight preference for moving (avoid idle) unless equally good.
        moved = 0 if (dx == 0 and dy == 0) else 1
        key = (rel, -dist_to_target if need_contest else -dist_to_target*0.5, d_opp1*0.01, moved, nx, ny)
        if best_key is None or key > best_key:
            best_key = key; best = [dx, dy]

    return best