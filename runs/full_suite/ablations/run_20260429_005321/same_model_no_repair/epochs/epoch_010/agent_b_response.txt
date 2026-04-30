def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx = 1 if sx < w // 2 else -1 if sx > w // 2 else 0
        ty = 1 if sy < h // 2 else -1 if sy > h // 2 else 0
        return [tx, ty]

    # Choose resource to "race": prefer those with best (self_dist - opp_dist)
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # smaller is better; add tiny tie-break on coordinates for determinism
        key = (ds - do, ds + do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    # Candidate moves: move towards target; avoid stepping into obstacles/outside.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer reducing distance to target
        d_to = man(nx, ny, rx, ry) - man(sx, sy, rx, ry)
        # Penalize near obstacles (1-step lookahead)
        near_pen = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in obs:
                near_pen += 1
        # Slightly reduce chance of moving toward opponent
        opp_pen = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        val = (d_to, near_pen, opp_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]