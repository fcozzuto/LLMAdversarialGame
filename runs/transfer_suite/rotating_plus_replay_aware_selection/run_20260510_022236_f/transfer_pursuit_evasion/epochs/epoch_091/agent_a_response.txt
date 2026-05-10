def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Simple 2-step lookahead to avoid local traps behind obstacles
    def bounded_reach_2(x, y):
        frontier = {(x, y)}
        for _ in range(2):
            nxt = set()
            for cx, cy in frontier:
                for dx, dy in moves:
                    nx, ny = cx + dx, cy + dy
                    if valid(nx, ny):
                        nxt.add((nx, ny))
            frontier = nxt
        return frontier

    best = None
    # Deterministic tie-break: prefer earlier in moves ordering
    for dx0, dy0 in moves:
        nx0, ny0 = sx + dx0, sy + dy0
        if not valid(nx0, ny0):
            continue

        dist_now = abs(nx0 - ox) + abs(ny0 - oy)
        reach = bounded_reach_2(nx0, ny0)

        # For evader: maximize minimum distance in reachable set; for pursuer: minimize it
        if is_evader:
            min_dist = min((abs(px - ox) + abs(py - oy) for px, py in reach), default=dist_now)
            score = (min_dist * 1000) + (dist_now)
            # discourage moving into tight spots
            score -= sum(1 for mx, my in moves if valid(nx0 + mx, ny0 + my)) == 0
        else:
            min_dist = min((abs(px - ox) + abs(py - oy) for px, py in reach), default=dist_now)
            score = (-min_dist * 1000) + (-dist_now)
            score += sum(1 for mx, my in moves if valid(nx0 + mx, ny0 + my)) * 0.01

        if best is None or score > best[0]:
            best = (score, dx0, dy0)

    if best is None:
        # All invalid (shouldn't happen); stay put
        return [0, 0]
    return [int(best[1]), int(best[2])]