def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x2 - x1
        if ax < 0:
            ax = -ax
        ay = y2 - y1
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def score_move(nx, ny):
        if (nx, ny) in blocked:
            return -10**9
        d = cheb(nx, ny, ox, oy)
        # Terminal avoidance/toward
        if not is_evader and d == 0:
            return 10**9
        if is_evader and d == 0:
            return -10**8
        # Obstacle-aware: prefer cells with more free neighbors (evader) or tighter (pursuer)
        free = 0
        for dx, dy in deltas:
            xx, yy = nx + dx, ny + dy
            if inb(xx, yy) and (xx, yy) not in blocked:
                free += 1
        # Corner-bias to stabilize escape lanes (evader) / commit lines (pursuer)
        phase = int(observation.get("turn_index", 0) or 0)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        cx, cy = corners[phase % 4]
        corner_dist = cheb(nx, ny, cx, cy)
        if is_evader:
            return d * 100 + free * 3 + corner_dist * 0.25
        else:
            return -d * 100 + (8 - free) * 3 - corner_dist * 0.25

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        candidates.append((score_move(nx, ny), dx, dy))

    if not candidates:
        return [0, 0]

    best = None
    for s, dx, dy in candidates:
        if best is None or s > best[0] or (s == best[0] and (dx, dy) < (best[1], best[2])):
            best = (s, dx, dy)
    return [int(best[1]), int(best[2])]