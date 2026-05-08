def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = (-1, 0, 1)
    moves = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target that we are likely to reach first; if we're behind, prefer nearer targets.
    best_r = None
    best_key = 10**18
    for rx, ry in res:
        dS = man(sx, sy, rx, ry)
        dO = man(ox, oy, rx, ry)
        behind = 0 if dS < dO else 1
        key = dS + 2 * behind - 0.25 * dO
        if key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    cur_dS = man(sx, sy, rx, ry)
    cur_dO = man(ox, oy, sx, sy)

    # Evaluate moves: get closer to target, reduce opponent's advantage, avoid letting opponent close on us too fast.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ndS = man(nx, ny, rx, ry)
        ndO = man(ox, oy, nx, ny)
        toward = cur_dS - ndS
        opp_change = cur_dO - ndO  # positive if we move away from opponent
        # If we're behind at the target, slightly prioritize intercepting (move that reduces our distance most).
        behind_factor = 1.0 if man(sx, sy, rx, ry) >= man(ox, oy, rx, ry) else 0.3
        v = behind_factor * (toward * 1.3) + (opp_change * 0.25) - (ndO * 0.03)
        if v > best_v or (v == best_v and (dx, dy) < best_m):
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]