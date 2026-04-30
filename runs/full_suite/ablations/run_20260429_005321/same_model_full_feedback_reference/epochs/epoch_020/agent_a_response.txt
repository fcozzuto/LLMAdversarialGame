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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def resource_target_preference():
        if not resources:
            return (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
        best_r = resources[0]
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            closer_me = (opd - myd)  # positive if I'm closer than opponent
            key = (-(closer_me), myd, abs(rx - ox) + abs(ry - oy), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        return best_r

    tx, ty = resource_target_preference()

    best = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Greedy: approach chosen target, but also deny opponent on that target region.
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Strongly prefer moves that keep me at/above opponent's progress to the target.
        lead = opd - myd
        # Secondary: prefer staying away from obstacles slightly (local penalty).
        wall_pen = 0
        for ex in (-1, 1):
            for ey in (-1, 1):
                ax, ay = nx + ex, ny + ey
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    wall_pen += 1

        # Tertiary: tie-break by moving deterministically (dx, dy ordering already).
        val = (-(lead), myd, wall_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]