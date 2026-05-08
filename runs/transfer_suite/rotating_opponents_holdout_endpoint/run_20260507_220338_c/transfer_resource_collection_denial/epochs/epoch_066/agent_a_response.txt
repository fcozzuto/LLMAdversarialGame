def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    resset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((p[0], p[1]))

    if (sx, sy) in resset:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target resource: prefer ones we can reach not worse than opponent, else closest "race".
    best = None
    best_key = None
    for rx, ry in resset:
        if (rx, ry) in obst:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive => we closer
        # Weight more as time runs out to commit; small tie-breaker favors nearer resource.
        timew = 1.0 + (40.0 / (turns_remaining + 10.0))
        key = (-adv * timew, sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Evaluate our possible move deltas by improving relative progress and reducing interference.
    opp_goal = (tx, ty)
    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            return x, y
        return nx, ny

    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nsx, nsy = next_pos(sx, sy, dx, dy)
        nosx, nosy = next_pos(ox, oy, dx, dy)  # approximate: we assume opponent could mirror delta

        our_d = man(nsx, nsy, tx, ty)
        opp_d = man(nosx, nosy, opp_goal[0], opp_goal[1])
        # Higher is better: larger distance gap and smaller absolute distance to target.
        score = (opp_d - our_d) * 10.0 - our_d * 0.1 + (man(ox, oy, tx, ty) - opp_d) * 0.05

        # Deterministic tie-break: prefer moves that reduce our distance most, then lexicographic.
        if best_score is None or score > best_score or (score == best_score and (our_d, dx, dy) < (man(next_pos(sx, sy, best_m[0], best_m[1])[0],
                                                                                                          next_pos(sx, sy, best_m[0], best_m[1])[1], tx, ty), best_m[0], best_m[1])):
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]