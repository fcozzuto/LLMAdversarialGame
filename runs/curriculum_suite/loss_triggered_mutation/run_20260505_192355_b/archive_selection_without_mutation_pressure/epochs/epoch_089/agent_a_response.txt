def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        margin = od - sd  # positive: we are closer
        center_bias = -0.05 * (abs(rx - cx) + abs(ry - cy))
        # If behind, reduce how badly; otherwise reward taking lead.
        key = (margin * 100 + center_bias - 0.2 * sd, -sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            deltas.append((dx, dy))
    # Prefer diagonal/horizontal/vertical deterministically: order by |dx| then |dy|
    deltas.sort(key=lambda d: (-abs(d[0]), -abs(d[1]), d[0], d[1]))

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in deltas + [(0, 0,)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        after_d = md(nx, ny, rx, ry)
        # If we are behind, also slightly favor reducing distance to opponent (intercept pressure).
        opp_after = md(nx, ny, ox, oy)
        sd_now = md(sx, sy, rx, ry)
        od_now = md(ox, oy, rx, ry)
        behind = 1 if (od_now - sd_now) < 0 else 0
        key = (-after_d, -behind * opp_after, abs(dx) + abs(dy), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]
        if dx == 0 and dy == 0:
            break

    return best_move