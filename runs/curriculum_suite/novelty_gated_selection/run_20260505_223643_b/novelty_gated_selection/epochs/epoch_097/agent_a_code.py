def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    res_set = set(resources)

    def mdist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    has_resources = len(resources) > 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource attraction
        if has_resources:
            best_d = 10**9
            for rx, ry in resources:
                d = mdist(nx, ny, rx, ry)
                if d < best_d:
                    best_d = d
            res_score = -best_d
            if (nx, ny) in res_set:
                res_score += 25
        else:
            # If no visible resources, drift to keep options: move away from opponent edges pressure
            res_score = 0

        # Opponent avoidance (keep distance)
        d_op = mdist(nx, ny, ox, oy)
        if d_op <= 2:
            opp_pen = 12
        elif d_op <= 3:
            opp_pen = 6
        elif d_op <= 4:
            opp_pen = 2
        else:
            opp_pen = 0

        # Mild bias: avoid mirroring opponent direction; encourage lateral spacing
        mir_bias = 0
        if ox != sx:
            mir_bias += 1 if (nx - sx) == 0 else 0
        if oy != sy:
            mir_bias += 1 if (ny - sy) == 0 else 0

        score = res_score - opp_pen + mir_bias
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is not None:
        return [best[1], best[2]]

    # Fallback: step toward center if possible, else stay
    cx, cy = w // 2, h // 2
    best2 = (-(10**9), 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = mdist(nx, ny, cx, cy)
            sc = -d
            if sc > best2[0]:
                best2 = (sc, dx, dy)
    return [best2[1], best2[2]]