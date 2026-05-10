def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    # Prefer resources where we are ahead; bias toward resources that also improve our "toward-center" progress.
    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # If opponent is already much closer, down-rank to avoid futile races.
        lead = (op_d - my_d)
        center_prog = (cheb(sx, sy, cx, cy) - cheb(rx, ry, cx, cy))
        # Also mildly prefer staying in our direction away from opponent to counter row sweeps.
        away = cheb(sx, sy, ox, oy) - cheb(rx, ry, ox, oy)
        key = (lead, center_prog + 0.15 * away, -my_d, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    dx0 = 0 if rx == sx else (1 if rx > sx else -1)
    dy0 = 0 if ry == sy else (1 if ry > sy else -1)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d_to_t = cheb(nx, ny, rx, ry)
                d_opp = cheb(nx, ny, ox, oy)
                # Greedy toward target, but prefer not to walk directly into opponent proximity.
                candidates.append((d_to_t, -d_opp, abs(dx - dx0) + abs(dy - dy0), dx, dy))
    candidates.sort()
    if candidates:
        _, _, _, dx, dy = candidates[0]
        return [int(dx), int(dy)]
    return [0, 0]