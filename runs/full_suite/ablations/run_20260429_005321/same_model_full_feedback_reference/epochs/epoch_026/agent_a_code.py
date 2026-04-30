def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax + ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_next = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal_next.append((dx, dy, nx, ny))
    if not legal_next:
        return [0, 0]

    # If opponent is closer to a resource, deprioritize it; prefer resources where we can be first.
    best = None
    for dx, dy, nx, ny in legal_next:
        if resources:
            best_adv = None
            best_res = None
            for rx, ry in resources:
                od = md(ox, oy, rx, ry)
                rd = md(nx, ny, rx, ry)
                adv = od - rd  # positive means we get closer than opponent (likely to intercept)
                if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_res):
                    best_adv = adv
                    best_res = (rx, ry)
            # Prefer maximizing advantage; also slightly reduce our distance to chosen target.
            score = (best_adv, -md(nx, ny, best_res[0], best_res[1]), -(dx != 0 or dy != 0), dx, dy)
        else:
            # No resources: head toward opponent but avoid obstacles already handled.
            score = (-(md(nx, ny, ox, oy)), -abs((nx + ny) - (w // 2 + h // 2)), dx, dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]