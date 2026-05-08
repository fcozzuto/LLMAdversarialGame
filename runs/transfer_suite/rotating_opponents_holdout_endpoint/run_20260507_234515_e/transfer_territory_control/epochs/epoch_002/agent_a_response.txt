def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = observation.get("obstacles", [])
    obstacles = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}
    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed = [(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2]
    self_terr = {(p[0], p[1]) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2}
    opp_terr = {(p[0], p[1]) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    near_obs = set()
    for (ax, ay) in obstacles:
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = ax + ddx, ay + ddy
                if in_bounds(nx, ny):
                    near_obs.add((nx, ny))

    opp_center_bias = man(ox, oy, cx, cy)
    # Prefer far-from-opponent expansion, but avoid stepping into opponent territory unless it also grabs unclaimed.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            if (nx, ny) not in self_terr:
                base = -8.0  # entering opponent land risks losing momentum
            else:
                base = 0.5
        else:
            base = 0.0

        if (nx, ny) in unclaimed:
            base += 6.0
        if (nx, ny) in self_terr:
            base += 1.5

        # Distance to opponent and to center controls whether we contest or sidestep their center pressure.
        d_opp = man(nx, ny, ox, oy)
        d_ctr = man(nx, ny, cx, cy)

        # If opponent is already near center, we try to push toward corners/edges (lower d_ctr, higher d_op).
        corner_pull = (man(nx, ny, 0, 0) + man(nx, ny, w - 1, h - 1) + man(nx, ny, 0, h - 1) + man(nx, ny, w - 1, 0)) / 4.0
        opp_factor = 1.0 if opp_center_bias < (w + h) * 0.8 else 0.6

        val = base + 0.9 * d_opp + 0.45 * corner_pull - opp_factor * 0.35 * d_ctr
        if (nx, ny) in near_obs:
            val -= 0.8
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]