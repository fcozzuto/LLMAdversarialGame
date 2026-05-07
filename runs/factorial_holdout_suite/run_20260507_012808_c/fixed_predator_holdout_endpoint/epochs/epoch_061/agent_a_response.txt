def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (0 <= x < w) and (0 <= y < h) and (x, y) not in obstacles:
                res_cells.append((x, y))
    if not res_cells:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(res_cells)) or len(res_cells))
    deny = 1.6 if rem <= 5 else 1.0

    best = None
    bestv = None
    bestd = None
    for x, y in res_cells:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        adv = od - sd
        v = (adv * 10.0 * deny) - (sd * 0.7) + (1.0 if sd == 0 else 0.0) + (0.02 * (w + h - sd))
        if bestv is None or v > bestv or (v == bestv and (sd < bestd)):
            bestv = v
            best = (x, y)
            bestd = sd

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w):
        dx = 0
    nx, ny = sx + dx, sy + dy
    if not (0 <= ny < h):
        dy = 0

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis move deterministically if diagonal blocked/invalid by obstacle
        axdx, axdy = dx, 0
        if 0 <= sx + axdx < w and (sx + axdx, sy) not in obstacles:
            return [axdx, 0]
        bydx, bydy = 0, dy
        if 0 <= sy + bydy < h and (sx, sy + bydy) not in obstacles:
            return [0, bydy]
        return [0, 0]

    return [int(dx), int(dy)]