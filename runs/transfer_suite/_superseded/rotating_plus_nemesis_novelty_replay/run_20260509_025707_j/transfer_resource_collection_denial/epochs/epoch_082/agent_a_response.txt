def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target with a stronger "take the lead" bias and a mild central tie-break.
    best_r = None
    best_v = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        # Prefer nearer resources if lead similar; if lead small/negative, still choose the most contestable.
        near_bias = -sd
        # Slightly weight corners less late to avoid last-moment thrash.
        center_bias = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        time_bias = (1.0 if tr <= 10 else 0.0) * (lead * 0.5)
        v = lead * 10.0 + near_bias * 1.5 + center_bias * 0.2 + time_bias
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    rx, ry = best_r
    # One-step deterministic policy: maximize expected advantage after move, also preventing obstacle traps.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        lead_after = od - sd

        # Secondary: if we are not the leader, prefer moves that improve lead the most.
        # Tertiary: avoid increasing distance to the chosen target.
        dist0 = man(sx, sy, rx, ry)
        step_improve = dist0 - sd

        # Tiny deterministic tie-break: lexicographic on (dx,dy) via ordering in dirs.
        score = lead_after * 12.0 + step_improve * 2.0 - sd * 0.05
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move