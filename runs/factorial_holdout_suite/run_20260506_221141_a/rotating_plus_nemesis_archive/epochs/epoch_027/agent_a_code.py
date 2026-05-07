def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources_raw = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick best contested resource: maximize our advantage and prefer closer overall.
    best = None
    for x, y in resources:
        my_d = man(sx, sy, x, y)
        op_d = man(ox, oy, x, y)
        score = (op_d - my_d, -my_d, x, y)  # higher is better by first term
        if best is None or score > best[0]:
            best = (score, (x, y))
    tx, ty = best[1]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_val = None

    # Greedy step toward target, with penalty for allowing opponent to be closer to target after the move.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_after = man(nx, ny, tx, ty)
        op_after = man(ox, oy, tx, ty)
        # Also lightly avoid getting too close to opponent (focus on resource collection).
        adv = op_after - my_after
        # Tie-break deterministically toward smallest distance to target, then toward larger x,y.
        val = (adv, -my_after, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]