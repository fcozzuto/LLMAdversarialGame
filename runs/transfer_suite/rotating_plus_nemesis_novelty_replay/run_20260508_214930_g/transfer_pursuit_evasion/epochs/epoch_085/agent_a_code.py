def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_evader = False

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    obstacles = list(obs)
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_pen(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for bx, by in obstacles:
            d = (nx - bx) * (nx - bx) + (ny - by) * (ny - by)
            if d < md:
                md = d
        if (nx, ny) in obs:
            return 10**6
        # Soft avoidance of nearby obstacles
        return (0 if md == 0 else 25 // max(1, md)) + (md <= 2) * 80

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        pen = obstacle_pen(nx, ny)
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if is_evader:
            # Run away while steering to safer central-ish space
            key = (-dist2, pen, center)
        else:
            # Pursue while avoiding obstacles and preferring moves that slightly reduce center distance
            key = (dist2, pen, center)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]