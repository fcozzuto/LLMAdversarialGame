def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def clear_md(x, y):
        if not obs: return 99
        best = 99
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best: best = d
        return best

    def sign(a): return 0 if a == 0 else (1 if a > 0 else -1)
    dx0, dy0 = sign(ox - sx), sign(oy - sy)

    # Pursuer tries to intercept where the evader likely goes next (away from pursuer).
    tx, ty = ox, oy
    if not is_evader:
        tx = ox + dx0
        ty = oy + dy0
        if tx < 0: tx = 0
        if tx >= w: tx = w - 1
        if ty < 0: ty = 0
        if ty >= h: ty = h - 1
    else:
        # Evader tries to run toward the corner farthest from pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        bestd = -1
        for cx, cy in corners:
            d = abs(cx - ox) + abs(cy - oy)
            if d > bestd:
                bestd = d
                bestc = (cx, cy)
        tx, ty = bestc

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - tx) + abs(ny - ty)
        c = clear_md(nx, ny)

        if is_evader:
            val = (-d, -c, dx, dy)  # maximize distance to pursuer-corner target, keep away from obstacles
        else:
            # minimize distance to intercepted target; prefer moves with more clearance to avoid getting boxed in
            val = (d, -c, dx, dy)

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move