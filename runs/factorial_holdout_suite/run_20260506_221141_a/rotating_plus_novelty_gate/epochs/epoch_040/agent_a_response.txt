def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def mdist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    # One-step lookahead: pick move that maximizes our advantage to best contested resource.
    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in blocked:
            nx, ny = sx, sy  # engine keeps us in place

        best_res_val = None
        for rx, ry in resources:
            sd = mdist(nx, ny, rx, ry)
            od = mdist(ox, oy, rx, ry)
            # Resource_denier: aggressively contest resources opponent is closer to.
            contested = 1 if od < sd else 0
            # Balance: large (od - sd), then prefer shorter self distance, then contested bonus.
            val = (od - sd) * 4 + contested * 6 - sd * 0.3
            if best_res_val is None or val > best_res_val:
                best_res_val = val

        # Tie-break deterministically: prefer moves with larger dx then dy (arbitrary but fixed)
        if best_val is None or best_res_val > best_val or (best_res_val == best_val and (dx, dy) > (best_move[0], best_move[1])):
            best_val = best_res_val
            best_move = [dx, dy]

    return best_move