def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])

    obs_set = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            obs_set.add((int(a["x"]), int(a["y"])))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    resources = []
    rset = set()
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            resources.append((x, y))
            rset.add((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) in rset:
            val = (-1, 0, 0, dx, dy)  # prioritize immediate pickup deterministically
        else:
            dmin = 10**9
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            val = (0, dmin, manh(nx, ny, sx, sy), dx, dy)
        if best is None or val < best:
            best = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]