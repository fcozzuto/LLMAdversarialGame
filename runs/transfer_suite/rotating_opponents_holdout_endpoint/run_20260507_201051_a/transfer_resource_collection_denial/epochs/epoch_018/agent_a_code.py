def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target that I can reach earlier, and if not possible, one that least favors the opponent.
    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        reach_adv = do - ds  # positive means I can get there first (or tie)
        key = (reach_adv, -ds, -man(ox, oy, rx, ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Greedy step: move toward target, with strong penalty for being closer to opponent and for obstacles.
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp_t = man(ox, oy, tx, ty)
        # Prefer decreasing my distance to target; if I can't be first, at least deny by not drifting toward opponent-favored resources.
        opp_favored = man(nx, ny, ox, oy)  # keep some separation to reduce contest swaps
        val = (-d_to_t, -opp_favored, d_opp_t, -dx, -dy)
        if best_val is None or val > best_val:
            best_val, best_step = val, (dx, dy)

    return [int(best_step[0]), int(best_step[1])]