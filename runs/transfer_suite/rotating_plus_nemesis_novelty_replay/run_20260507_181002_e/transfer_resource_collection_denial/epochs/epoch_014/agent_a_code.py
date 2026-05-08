def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                obs_set.add((int(q[0]), int(q[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                resources.append((int(q[0]), int(q[1])))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if (sx, sy) in resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        best_target = None
        best_val = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Favor closer resources while deprioritizing ones the opponent can reach quickly.
            val = (-ds) + 0.35 * do - 0.01 * (ds * ds)
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_target):
                best_val = val
                best_target = (rx, ry)

        tx, ty = best_target
        best_move = None
        best_mval = None
        for dx, dy, nx, ny in moves:
            dself = man(nx, ny, tx, ty)
            dop = man(nx, ny, ox, oy)
            # Primary: get closer to target; Secondary: keep away from opponent for races.
            mval = (-dself) + 0.08 * dop
            if best_mval is None or mval > best_mval:
                best_mval = mval
                best_move = (dx, dy)
            elif mval == best_mval:
                # Deterministic tiebreak: prefer smaller distance, then lexicographic move
                if man(nx, ny, tx, ty) < man(sx + best_move[0], sy + best_move[1], tx, ty):
                    best_move = (dx, dy)
                elif man(nx, ny, tx, ty) == man(sx + best_move[0], sy + best_move[1], tx, ty):
                    if (dx, dy) < best_move:
                        best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move to maximize distance from opponent, avoid obstacles.
    best_move = None
    best_d = None
    for dx, dy, nx, ny in moves:
        d = man(nx, ny, ox, oy)
        if best_d is None or d > best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]