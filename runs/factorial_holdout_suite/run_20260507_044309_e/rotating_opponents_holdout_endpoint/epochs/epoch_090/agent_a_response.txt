def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**18
    best_lex = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        cur_best = -10**18
        cur_t = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier / keep advantage; penalize distance.
            val = (opd - myd) * 4 - myd
            if val > cur_best:
                cur_best = val
                cur_t = (rx, ry)
            elif val == cur_best and cur_t is not None:
                # Deterministic tie-break: lower myd, then lexicographic target.
                if myd < man(nx, ny, cur_t[0], cur_t[1]) or (myd == man(nx, ny, cur_t[0], cur_t[1]) and (rx, ry) < cur_t):
                    cur_t = (rx, ry)
        if cur_t is None:
            continue
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
            best_lex = cur_t
        elif cur_best == best_val:
            # Break ties consistently by preferring the move that targets lexicographically smaller resource,
            # then by smaller |dx|+|dy| (i.e., less deviation).
            if best_lex is None or cur_t < best_lex or (cur_t == best_lex and (abs(dx) + abs(dy)) < (abs(best_move[0]) + abs(best_move[1]))):
                best_move = (dx, dy)
                best_lex = cur_t

    return [int(best_move[0]), int(best_move[1])]