def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        od = manh(ox, oy, rx, ry)
        sd = manh(sx, sy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # maximize advantage, then closer, then deterministic
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    dx_opt = 0
    dy_opt = 0
    if tx != sx:
        dx_opt = -1 if tx < sx else 1
    elif ty != sy:
        dy_opt = -1 if ty < sy else 1

    pref = []
    if dx_opt != 0:
        pref.append((dx_opt, 0))
        pref.append((0, -1 if ty < sy else 1))
    if dy_opt != 0:
        pref.append((0, dy_opt))
        pref.append((-1 if tx < sx else 1, 0))
    pref.append((dx_opt, 0))
    pref.append((0, dy_opt))
    pref.append((0, 0))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_step(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return -10**18
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        return (opd - myd, -myd, -nx, -ny)

    checked = set()
    for dx, dy in pref:
        if (dx, dy) in checked:
            continue
        checked.add((dx, dy))
        if valid(sx + dx, sy + dy):
            best_dx, best_dy = dx, dy
            best_val = score_step(dx, dy)
            # keep deterministic, no need to check all
            if best_val > -10**17:
                return [int(dx), int(dy)]

    best_dx, best_dy = 0, 0
    best_val = -10**18
    for dx, dy in moves:
        if (dx, dy) in checked:
            continue
        if not valid(sx + dx, sy + dy):
            continue
        v = score_step(dx, dy)
        if v > best_val:
            best_val = v
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]