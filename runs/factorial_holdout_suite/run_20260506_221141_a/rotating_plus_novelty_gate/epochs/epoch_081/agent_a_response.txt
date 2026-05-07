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

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_towards(tx, ty):
        best = (0, 0)
        best_score = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    pass
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    sd = mhd(nx, ny, tx, ty)
                    od = mhd(ox, oy, tx, ty)
                    opp_adv = od - sd
                    # prefer reducing distance; break ties by increasing opp_adv and moving off parity deadlocks
                    score = 1000 * (-sd) + 10 * opp_adv + (-( (nx + ny) & 1 ))
                    if score > best_score:
                        best_score = score
                        best = (dx, dy)
        return [best[0], best[1]]

    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        # maximize (od - sd); tie-break: smaller sd; tie-break: larger "danger" to opponent (closer for them)
        key = (od - sd, -sd, od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    return step_towards(best_rx, best_ry)