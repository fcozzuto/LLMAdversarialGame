def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic fallback: move to increase distance from opponent while not stepping into obstacle.
        best = (0, [0, 0])
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (dx or dy) and (sx, sy) in obstacles:
                    continue
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = man(nx, ny, ox, oy)
                if d > best[0]:
                    best = (d, [dx, dy])
        return best[1]

    # Target selection: prefer resources we can contest (opp closer disadvantage), then closest-to-us.
    best_r = None
    best_s = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Quadrant bias: push toward our side (bottom-left), since opponent starts opposite.
        quad = 0
        if rx <= (w - 1) // 2 and ry <= (h - 1) // 2:
            quad = 1
        if rx >= (w - 1) // 2 and ry >= (h - 1) // 2:
            quad = -1
        score = (od - sd) + 2 * quad - 0.15 * sd
        if best_s is None or score > best_s:
            best_s = score
            best_r = (rx, ry)

    tx, ty = best_r
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            self_to = man(nx, ny, tx, ty)
            opp_dist = man(nx, ny, ox, oy)
            # Tie-break deterministic: prioritize reducing distance to target, then increasing distance from opponent.
            candidates.append((self_to, -opp_dist, dx, dy))
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]