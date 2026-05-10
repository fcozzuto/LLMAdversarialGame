def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" not in self_role and "evad" in opp_role)

    dxs = (-1, 0, 1)
    deltas = [[dx, dy] for dx in dxs for dy in dxs]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]) == 0, d[0], d[1]))  # keep deterministic
    if [0, 0] in deltas:
        deltas = [d for d in deltas if d != [0, 0]] + [[0, 0]]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = None

    vx0, vy0 = ox - sx, oy - sy
    primary_axis = 0 if abs(vx0) >= abs(vy0) else 1  # 0=x, 1=y

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        d = dist(nx, ny, ox, oy)
        # Corner bias for determinism: prefer far/near corners depending on role.
        corner_near = (nx in (0, w - 1) and ny in (0, h - 1))
        corner_far = corner_near  # same set; sign handled below

        # Alignment: favor reducing larger coordinate difference first.
        ax = abs(ox - nx)
        ay = abs(oy - ny)
        align = (abs(ox - sx) - ax) if primary_axis == 0 else (abs(oy - sy) - ay)

        if is_pursuer:
            # pursue: maximize improvement toward opponent; discourage moves that stall both axes
            # v is higher-better
            stalled = (ax == abs(vx0)) and (ay == abs(vy0))
            v = (-d) + 0.05 * align + (0.02 if corner_near else 0.0) - (0.3 if stalled else 0.0)
        else:
            # evade: maximize distance and keep moving away along the primary axis
            v = d + 0.05 * (-align) + (0.02 if corner_far else 0.0)

        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move