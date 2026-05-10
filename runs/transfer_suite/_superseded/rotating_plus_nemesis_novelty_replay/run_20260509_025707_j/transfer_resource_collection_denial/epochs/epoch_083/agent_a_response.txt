def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b, c, e):
        return abs(a - c) + abs(b - e)

    if not resources:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)

    # Pick a resource that maximizes expected dominance margin over opponent,
    # with a slight bias toward the one we can reach sooner.
    best_r = None
    best_r_val = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        myd = d(sx, sy, rx, ry)
        opd = d(ox, oy, rx, ry)
        margin = opd - myd  # positive means we're closer
        soon = 7 - min(7, myd)  # earlier is better
        # If low turns left, prioritize immediate capture more strongly.
        time_weight = 1 + (8 - min(8, tr)) * 0.25
        val = margin * (2.0 if margin > 0 else 1.0) + soon * time_weight
        # Break ties toward nearer-to-opponent (deny harder)
        tie = (opd, myd, rx, ry)
        if best_r is None or val > best_r_val or (val == best_r_val and tie < (best_r[1], best_r[2], best_r[3], best_r[4])):
            best_r = [rx, ry, myd, opd, rx]
            best_r_val = val

    tx, ty = best_r[0], best_r[1]

    # Move by choosing the delta that maximizes next-step dominance improvement,
    # not just distance-to-target (helps against sweep behaviors).
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cur_self = d(sx, sy, tx, ty)
        cur_opp = d(ox, oy, tx, ty)
        nxt_self = d(nx, ny, tx, ty)
        nxt_opp = d(ox, oy, tx, ty)
        dom_gain = (cur_opp - cur_self) - (nxt_opp - nxt_self)  # negative is good (we reduce opponent advantage)
        dom_improve = -dom_gain

        # Secondary: after moving, prefer cells that keep us closer overall to a small set
        # of nearest resources (deterministic, no full search).
        # Take up to 3 nearest-by-Manhattan to current position.
        scored = []
        for r in resources:
            rx, ry = r[0], r[1]
            md = d(sx, sy, rx, ry)
            scored.append((md, rx, ry))
        scored.sort(key=lambda t: (t[0], t[1], t[2]))
        local = scored[:3]
        loc_val = 0
        for _, rx, ry in local:
            loc_val += (d(ox, oy, rx, ry) - d(nx, ny, rx, ry))
        # If turns are low, also prefer immediate approach to target.
        close_bias = (6 - min(6, nxt_self)) * (1.0 + (8 - min(8, tr)) * 0.15)

        val = dom_improve * 2.0 + loc_val + close_bias
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move