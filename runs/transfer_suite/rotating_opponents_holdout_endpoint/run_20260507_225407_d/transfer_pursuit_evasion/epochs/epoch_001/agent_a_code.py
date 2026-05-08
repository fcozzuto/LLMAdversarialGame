def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role) or ("catch" in role)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            cheb = max(abs(nx - ox), abs(ny - oy))
            man = abs(nx - ox) + abs(ny - oy)
            candidates.append((nx, ny, dx, dy, cheb, man))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: prefer smaller dx then smaller dy (consistent ordering)
    candidates.sort(key=lambda t: (t[4], t[5], t[2], t[3])) if is_pursuer else candidates.sort(key=lambda t: (-t[4], -t[5], t[2], t[3]))
    # Additional pursuer pressure: bias toward reducing both distance and staying clear of obstacles by preferring moves with more free neighbors.
    if is_pursuer:
        def free_neighbors(nx, ny):
            c = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    tx, ty = nx + ddx, ny + ddy
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                        c += 1
            return c
        candidates.sort(key=lambda t: (t[4], t[5], -free_neighbors(t[0], t[1]), t[2], t[3]))
    else:
        # Evader pressure: if multiple max-distance moves exist, prefer moving toward the farther corner opposite opponent.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        ax, ay = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))
        def corner_bias(nx, ny):
            return max(abs(nx - ax), abs(ny - ay))
        candidates.sort(key=lambda t: (-t[4], -t[5], -corner_bias(t[0], t[1]), t[2], t[3]))

    return [int(candidates[0][2]), int(candidates[0][3])]