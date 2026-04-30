def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    ti = int(observation.get("turn_index", 0) or 0)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deterministic target: maximize our advantage in reaching it.
    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # small tie-break: prefer nearer/central-ish, and alternate preference by turn
        center_bias = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
        s = (od - sd) * 10.0 + center_bias * 0.01 + (0.001 if ((rx + ry + ti) & 1) == 0 else 0.0)
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    tx, ty = best_r

    # Choose move that best improves our distance while not letting opponent get better.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**12  # discourage moving into obstacles
        else:
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            # opponent may still contest; reward pushing them away from the same target
            opp_push = (no - cheb(ox, oy, tx, ty)) * 0.0
            val = (best_s) + (no - ns) * 5.0 + opp_push
            # extra heuristic: prefer moves that reduce our distance and avoid worsening it
            val += (-ns) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]