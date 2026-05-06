def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    rlist = [(int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]
    rlist = [(rx, ry) for (rx, ry) in rlist if inb(rx, ry) and (rx, ry) not in obs]
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Choose a "winnable" resource: prioritize where we are closer than opponent, else deny by approaching.
    best_score = None
    best_target = None
    for rx, ry in rlist:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # margin > 0 means we likely arrive first; tie-break by farther potential
        margin = do - ds
        potential = 1.0 / (1 + ds)
        # Encourage moving toward opponent side early (deterministic bias)
        side_bias = (rx - sx) * (1 if ox > sx else -1) + (ry - sy) * (1 if oy > sy else -1)
        score = (margin * 10.0) + (potential * 3.0) + (side_bias * 0.01)
        if best_score is None or score > best_score:
            best_score, best_target = score, (rx, ry)

    tx, ty = best_target

    # Next move: minimize distance to target, but avoid stepping into a near-opponent trap.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds1 = md(nx, ny, tx, ty)
        # trap penalty if opponent is very close after our move
        do1 = md(ox, oy, tx, ty)
        # If opponent is closer to our candidate move than we are, discourage that move.
        self_to = ds1
        opp_to = md(ox, oy, nx, ny)
        trap = (opp_to - self_to) if opp_to < self_to else 0
        val = (-ds1) + (trap * -2.5) + (0.001 * ((nx - tx) + (ny - ty)))
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]