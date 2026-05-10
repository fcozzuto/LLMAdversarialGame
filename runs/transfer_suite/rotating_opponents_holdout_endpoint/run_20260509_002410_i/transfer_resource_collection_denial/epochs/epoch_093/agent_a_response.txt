def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    best_val = -10**18

    # Prefer resources we can reach no later than opponent; otherwise fall back to nearest.
    fallback_t = None
    fallback_d = 10**9
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        if d_me <= d_opp:
            val = (d_opp - d_me) * 1000 - d_me  # big lead first, then quicker
            if val > best_val:
                best_val = val
                best = (rx, ry)
        else:
            if d_me < fallback_d:
                fallback_d = d_me
                fallback_t = (rx, ry)

    target = best if best is not None else fallback_t
    if target is None:
        target = resources[0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct diagonal/axis move; if blocked, try deterministic alternatives.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for mvx, mvy in candidates:
        nx = sx + mvx
        ny = sy + mvy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mvx), int(mvy)]
    return [0, 0]