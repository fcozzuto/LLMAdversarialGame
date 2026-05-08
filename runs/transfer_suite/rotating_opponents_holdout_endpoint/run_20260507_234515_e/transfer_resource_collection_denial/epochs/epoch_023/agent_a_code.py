def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If no resources, head toward center.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -kdist(nx, ny, cx, cy) + 0.01 * (kdist(nx, ny, ox, oy))
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    # Target selection: prefer resources where we are closer than opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        myd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Higher is better: we want myd < od. Add tie-break by earlier advantage and distance.
        adv = (od - myd)
        sc = adv * 1000 - myd * 2 + (od * 0.1)
        key = (sc, -adv, -od, -myd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Move: choose step that most improves distance to target while keeping away from opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = kdist(nx, ny, tx, ty)
        d_opp = kdist(nx, ny, ox, oy)
        # Primary: reduce distance to target. Secondary: increase distance from opponent.
        score = -d_self * 10 + d_opp * 1 + (0 if (nx, ny) == (tx, ty) else -0.01 * kdist(nx, ny, sx, sy))
        key = (score, -d_opp, -d_self, dx, dy)
        if score > best_score or (score == best_score and key > (best_score,)):
            best_score = score
            best_move = [dx, dy]

    return best_move