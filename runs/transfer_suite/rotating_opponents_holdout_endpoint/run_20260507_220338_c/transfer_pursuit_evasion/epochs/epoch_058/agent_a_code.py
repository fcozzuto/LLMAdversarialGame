def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy  # engine would keep us in place on invalid
        d = cheb(nx, ny)
        # small wall-aware heuristic: prefer staying away from obstacles when evading
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in blocked:
                    near_obs += 1
        corner_bias = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)  # farther from center
        val = d
        if is_evader:
            val = (val, corner_bias, -near_obs)
            better = best_val is None or val > best_val
        else:
            val = (-d, -near_obs, -(corner_bias))  # chase distance, avoid clutter
            better = best_val is None or val > best_val
        if better:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]