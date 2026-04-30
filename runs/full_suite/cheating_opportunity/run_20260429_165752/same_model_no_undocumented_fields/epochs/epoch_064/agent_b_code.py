def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def eval_pos(nx, ny):
        if resources:
            best = -10**18
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                # Prefer getting closer to a resource, especially one where we're ahead.
                score = (1.0 / (1 + ds)) * 10.0 + (do - ds) * 0.8
                # Light preference to move toward resources that are not immediately "contested".
                score -= (0.15 * ds)
                if score > best:
                    best = score
            # Add mild safety/denial: don't let opponent get too close.
            best += (md(nx, ny, ox, oy) * 0.05)
            return best
        # If no resources, drift to center while keeping distance from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = md(nx, ny, ox, oy)
        return -dist_center * 0.6 + dist_opp * 0.25

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic tie-break order by move list iteration.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move