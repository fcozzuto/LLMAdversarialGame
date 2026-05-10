def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Opponent threat: how close opponent can get to its best option
    def opp_best_dist(px, py):
        best = 10**9
        for rx, ry in resources:
            if ok(rx, ry):
                d = man(px, py, rx, ry)
                if d < best:
                    best = d
        return best if best != 10**9 else 10**6

    # Deterministic "assignment": pick a target that maximizes lead and also pushes into our direction.
    # Our direction: towards the opposite corner from the opponent start bias.
    dirx = 1 if sx < ox else -1
    diry = 1 if sy < oy else -1

    best_target = None
    best_tscore = -10**18
    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds
        # Prefer targets that progress us in our direction (not just close).
        prog = (rx - sx) * dirx + (ry - sy) * diry
        tscore = 1000 * lead + 2 * prog - ds
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)
    if best_target is None:
        return [0, 0]

    tx, ty = best_target

    # Choose the move that (1) improves our race to the target, (2) reduces opponent's best threat,
    # (3) breaks ties by moving closer and (4) avoids obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curr_opp_threat = opp_best_dist(ox, oy)

    best = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        ns = man(nx, ny, tx, ty)
        # Encourage capturing soon; severe penalty if we fall behind on the target.
        target_lead = curr_opp_threat - ns  # proxy for "how soon we are relative to opponent's best"
        # Reduce opponent's threat by moving into positions that generally increase their distances.
        # (No pathfinding; use delta on best-distance-to-resources as a cheap proxy.)
        new_opp_threat = opp_best_dist(ox, oy)
        opp_delta = curr_opp_threat - new_opp_threat  # likely 0, but keep deterministic structure

        # Tie-break: closer to target, then prefer moving in our direction.
        prog2 = (nx - sx) * dirx + (ny - sy) * diry
        score = 50 * target_lead + opp_delta - 3 * ns + prog2

        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best