def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target selection: prefer resources we're (materially) closer to; else steal nearest we can reach quickly.
    best_target = None
    best_gap = -10**9
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        gap = myd - opd  # negative means we're closer
        # small bias for central-ish resources to reduce opponent racing in corners
        center_bias = -0.1 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        val = -gap + center_bias
        if gap <= 0:
            val += 1.5
        if (rx, ry) == (sx, sy):
            val += 10**6
        if val > best_gap:
            best_gap = val
            best_target = (rx, ry)

    rx, ry = best_target

    # Move scoring: push toward chosen target, but avoid stepping into opponent "front"
    # by discouraging moves that reduce opponent->target advantage.
    best = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in candidates:
        myd = dist(nx, ny, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # how much our move worsens/betters our race relative to opponent reaching the same target
        myd_from_now = dist(nx, ny, rx, ry)
        opd_to_us = dist(ox, oy, nx, ny)
        # Also include a repulsion from opponent to prevent allowing grabs in short distance
        opp_repulse = 0
        if opd_to_us <= 2:
            opp_repulse = -2.0 * (3 - opd_to_us)
        # Avoid drifting toward opponent when we aren't winning the race
        gap_here = myd_from_now - dist(ox, oy, rx, ry)
        race = 0
        if gap_here <= 0:
            race += 3.0
        else:
            race -= 1.2 * gap_here
        # encourage capturing immediately
        capture = 10**6 if (nx, ny) == (rx, ry) else 0
        score = (-myd) + 0.2 * (opd - myd) + race + opp_repulse + capture
        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]