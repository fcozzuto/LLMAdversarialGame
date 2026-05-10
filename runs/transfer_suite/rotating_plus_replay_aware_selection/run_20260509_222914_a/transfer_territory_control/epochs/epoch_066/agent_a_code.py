def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def md(a, b, c, d):
        x = a - c
        y = b - d
        return (x if x >= 0 else -x) + (y if y >= 0 else -y)

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    best = (None, -10**9)

    opp_d = md(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dist_opp = md(nx, ny, ox, oy)
        if resources:
            mind = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score = 1000 - 10 * mind
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -md(nx, ny, cx, cy)
        if opp_d <= 2:
            score += 30 * dist_opp
        score += dist_opp
        if score > best[1]:
            best = ([dx, dy], score)

    if best[0] is not None:
        return best[0]

    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]