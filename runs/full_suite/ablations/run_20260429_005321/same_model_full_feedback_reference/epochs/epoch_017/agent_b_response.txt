def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_dxdy = [0, 0]

    if resources:
        for dx, dy, nx, ny in candidates:
            best_target_metric = None
            for rx, ry in resources:
                our_d = md(nx, ny, rx, ry)
                opp_d = md(ox, oy, rx, ry)
                if our_d < 0 or opp_d < 0:
                    continue
                # Prefer resources where we're closer than opponent, strongly.
                metric = (opp_d - our_d) * 100 - our_d
                if best_target_metric is None or metric > best_target_metric:
                    best_target_metric = metric
            # If all targets exist, best_target_metric always set.
            # Add a mild preference to avoid drifting too far from center after targeting.
            center_pen = md(nx, ny, cx, cy)
            value = (best_target_metric if best_target_metric is not None else -10**9) - center_pen
            if best is None or value > best:
                best = value
                best_dxdy = [dx, dy]
    else:
        # No resources visible: move to reduce opponent advantage by heading toward center
        # while not allowing easy pursuit.
        for dx, dy, nx, ny in candidates:
            value = -md(nx, ny, cx, cy) + (md(nx, ny, ox, oy) // 2)
            if best is None or value > best:
                best = value
                best_dxdy = [dx, dy]

    return best_dxdy