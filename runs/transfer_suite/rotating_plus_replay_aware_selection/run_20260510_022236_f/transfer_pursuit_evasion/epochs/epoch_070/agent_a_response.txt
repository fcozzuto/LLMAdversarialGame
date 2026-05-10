def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    if is_evader:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
            cn = max(corners, key=lambda c: abs(c[0]-nx) + abs(c[1]-ny))
            wall_bias = abs(cn[0]-nx) + abs(cn[1]-ny)
            val = d + 0.05 * wall_bias
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # Pursuer: greedy with 2-step lookahead to avoid getting blocked by obstacles
        def score(px, py):
            return -((px - ox) * (px - ox) + (py - oy) * (py - oy))

        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # If moving directly into capture range would be handled by engine; here just maximize closeness.
            val = score(nx, ny)
            # 2-step lookahead for pursuer only, deterministic
            for dx2, dy2 in moves:
                mx, my = nx + dx2, ny + dy2
                if not ok(mx, my):
                    continue
                # Encourage approach and discourage stalling
                val2 = score(mx, my) + 0.01 * (abs(mx - sx) + abs(my - sy))
                if val2 > val:
                    val = val2
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move