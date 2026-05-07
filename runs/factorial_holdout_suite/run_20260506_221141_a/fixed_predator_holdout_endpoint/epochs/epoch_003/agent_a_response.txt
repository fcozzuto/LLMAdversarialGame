def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    ahead = []
    behind = []
    for rx, ry in resources:
        selfd = md(x, y, rx, ry)
        oppd = md(ox, oy, rx, ry)
        if selfd <= oppd:
            ahead.append((selfd, rx, ry))
        else:
            behind.append((oppd, selfd, rx, ry))

    if ahead:
        _, tx, ty = min(ahead, key=lambda t: (t[0], t[1], t[2]))
    else:
        # If we can't beat them to any resource, pick one that is hard for the opponent (largest oppd)
        # while not too far from us (tie-break by smaller selfd).
        _, selfd, tx, ty = max(behind, key=lambda t: (t[0], -t[1], -t[2], -t[3]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_val = None
    best_move = [0, 0]
    self_cur = md(x, y, tx, ty)
    opp_cur = md(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        self_next = md(nx, ny, tx, ty)
        opp_next = md(ox, oy, tx, ty)  # opponent static for step evaluation
        # Main: reduce distance to target.
        val = (self_cur - self_next) * 3
        # Secondary: if behind to the target, keep more distance from opponent to reduce denial swings.
        if self_cur > opp_cur:
            val += (md(nx, ny, ox, oy) - md(x, y, ox, oy)) * 0.8
        # Tertiary: avoid stepping closer to opponent unless we are already winning the target.
        if self_cur <= opp_cur:
            val += (md(nx, ny, ox, oy) - md(x, y, ox, oy)) * 0.1
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]