def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if (x, y) in resources:
        return [0, 0]

    # Target selection: deterministic opponent-aware advantage; then prefer faster (lower ds); then stable coords.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive => we are closer or equal
        # If we are not closer, still consider, but deprioritize strongly.
        closer_bonus = 1 if lead > 0 else 0
        key = (closer_bonus, lead, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    # Fallback: head to center.
    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    # Greedy move with obstacle avoidance; also avoid walking toward opponent when tied on target progress.
    cur_d = cheb(x, y, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        obs_pen = -8 if (nx, ny) in obstacles else 0
        nd = cheb(nx, ny, tx, ty)

        # Primary: reduce distance to target (more is better).
        gain = cur_d - nd

        # Secondary: if opponent is also close to the target, don't give them easy access by moving away from optimal lanes.
        # We approximate by adding a term that prefers increasing distance between us and opponent when gain is small.
        opp_dist_now = cheb(x, y, ox, oy)
        opp_dist_next = cheb(nx, ny, ox, oy)
        opp_term = (opp_dist_next - opp_dist_now) if gain <= 0 else 0

        # Tertiary: avoid stepping onto resources/opponent unless it is the target.
        resource_step = 1 if (nx, ny) in resources else 0
        step_target = 1 if (nx, ny) == (tx, ty) else 0

        # Ensure deterministic tie-break with coordinates.
        val = (gain, opp_term, step_target, resource_step, obs_pen, -nd, -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]