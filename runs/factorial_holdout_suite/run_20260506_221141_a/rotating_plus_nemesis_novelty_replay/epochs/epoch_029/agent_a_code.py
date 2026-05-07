def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # Prefer making the opponent worse: higher (od - sd)
        val = od - sd
        # Tie-breaker: prefer closer to us when equally deniable
        t = -sd
        if best_val is None or (val, t) > best_val:
            best_val = (val, t)
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_step = None
    best_step_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue
        sd = manh(nx, ny, tx, ty)
        od = manh(ox, oy, tx, ty)
        val = (od - sd, -sd, dx, dy)
        if best_step_val is None or val > best_step_val:
            best_step_val = val
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]