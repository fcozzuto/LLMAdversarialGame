def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_sc = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -cheb(nx, ny, cx, cy) + 0.02 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, [dx, dy]
        return best

    # Prefer resources where we are closer than opponent, also with deterministic tie breaks.
    center_x, center_y = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        self_d_to_best = 10**9
        opp_d_to_best = 10**9
        corner_bias = 0
        # Corner bias: prefer resources closer to our starting corner if scores tie
        corner_bias = -cheb(nx, ny, w - 1 if sx > w // 2 else 0, h - 1 if sy > h // 2 else 0)

        best_local = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Main goal: maximize lead (opponent distance - self distance)
            lead = od - sd
            # Secondary: prefer shorter self distance and slightly prefer central routes deterministically
            sc = lead * 1000 - sd * 3 - cheb(nx, ny, center_x, center_y) * 0.1
            # Deterministic tie-break: smaller (rx,ry) lexicographically
            if sc > best_local:
                best_local = sc
                self_d_to_best = sd
                opp_d_to_best = od

        # Add slight preference for keeping distance from opponent when leads are equal
        opp_sp_dist = cheb(nx, ny, ox, oy)
        total = best_local + (opp_sp_dist * 0.02) + corner_bias * 0.01

        if total > best_score:
            best_score = total
            best_move = [dx, dy]

    return best_move