def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def corner_bias(x, y):
        # We start opposite corner (agent_b typically near bottom-right); bias toward center to avoid being trapped.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -((abs(x - cx) + abs(y - cy)))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; if both can reach, pick one where we reduce lead for opponent.
            lead = do - ds
            dist_to_self = ds
            dist_to_opp = do
            # Tie-break deterministically by position
            key = (lead, -dist_to_self, -dist_to_opp, -rx - ry, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # If opponent is already much closer to target, shift to a "second" target that we can contest.
    ds_t = cheb(sx, sy, tx, ty)
    do_t = cheb(ox, oy, tx, ty)
    if resources and do_t <= ds_t:
        best2 = (tx, ty)
        best_key2 = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            key = (lead, -ds, rx, ry)  # deterministic
            if best_key2 is None or key > best_key2:
                best_key2 = key
                best2 = (rx, ry)
        tx, ty = best2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score: reduce distance to target; slight preference to keep moving (avoid being stagnant if possible).
        v = -cheb(nx, ny, tx, ty) + 0.02 * corner_bias(nx, ny) - (0.001 if dx == 0 and dy == 0 else 0.0)
        # Also penalize moving closer to a resource that opponent is closer to (avoid gifts).
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) <= cheb(sx, sy, rx, ry):
                v -= 0.03 if cheb(nx, ny, rx, ry) < cheb(sx, sy, rx, ry) else 0.0