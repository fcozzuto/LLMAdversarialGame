def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Target: prefer resources we can reach first; if none, prefer least-losing.
    best = resources[0]
    bestv = -10**18
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd
        v = lead * 1200 - sd
        # tiny tie-break: closer to center to reduce corner-locks vs diagonal probing
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v -= (abs(rx - cx) + abs(ry - cy)) * 1.0
        if v > bestv:
            bestv = v
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = deltas[4]
    best_step_v = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # Prefer reducing distance to target while increasing our lead; also mildly avoid giving opponent an easy route.
        lead2 = od2 - sd2
        v = lead2 * 1200 - sd2
        v += (md(nx, ny, tx, ty) == 0) * 100000
        # Block/contest: step that increases opponent-target distance more is better.
        v += -(md(ox, oy, nx, ny)) * 0.01
        if v > best_step_v:
            best_step_v = v
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]