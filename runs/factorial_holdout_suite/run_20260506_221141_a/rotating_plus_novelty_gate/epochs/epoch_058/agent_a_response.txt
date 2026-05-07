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
    res_set = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked and (x, y) not in res_set:
                resources.append((x, y))
                res_set.add((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_adv(px, py):
        best = -10**9
        for rx, ry in resources:
            sd = kdist(px, py, rx, ry)
            od = kdist(ox, oy, rx, ry)
            if sd == 0:
                adv = 10**9  # immediate pickup
            else:
                adv = (od - sd) * 100 - sd  # prefer where we beat opponent by distance, then close
            if adv > best:
                best = adv
        return best

    # Look one step ahead and also avoid stepping into obstacles/bounds.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            val = -10**17
        else:
            val = best_adv(nx, ny)
            # small deterministic tie-break: keep closer to center band to reduce stalling
            center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
            val = val + int(center_bias)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]