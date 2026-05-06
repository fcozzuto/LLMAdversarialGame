def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    if not resources:
        return [0, 0]

    best_val = None
    best_move = [0, 0]

    # Resource-denial style: choose next step maximizing the arrival advantage
    # (opponent distance - our distance) over the best resource for that step.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        step_best = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources we can beat, and in ties prefer those farther from opponent.
            val = (od - sd) * 100 - sd + (od) * 0.5
            # Mild preference to keep moving toward the opponent's general side (deny lanes)
            if (rx - sx) * (rx - ox) < 0:
                val += 0.25
            if step_best is None or val > step_best:
                step_best = val
        if best_val is None or step_best > best_val:
            best_val = step_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]