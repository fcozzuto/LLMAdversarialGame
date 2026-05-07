def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs_list))
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(sx, sy, rx, ry)
            if sd == 0:
                return [0, 0]
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer.
            # Key: (advantage, our distance, opponent distance, resource position)
            key = (od - sd, -sd, -od, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (w // 2, h // 2)

    curd = cheb(sx, sy, tx, ty)
    best_step = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Score: reduce distance to target, tie-break away from opponent if possible.
        od = cheb(ox, oy, tx, ty)
        score = (curd - nd, -(abs(ox - nx) + abs(oy - ny)) , -(nd), -od)
        if best_score is None or score > best_score:
            best_score = score
            best_step = [dx, dy]
    return best_step