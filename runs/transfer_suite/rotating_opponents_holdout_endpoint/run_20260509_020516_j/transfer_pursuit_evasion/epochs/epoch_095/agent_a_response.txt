def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    if not (0 <= sx < w and 0 <= sy < h) or (sx, sy) in obstacles:
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))
        if (sx, sy) in obstacles:
            for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    sx, sy = nx, ny
                    break

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score(nx, ny):
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_bias = -edge if is_evader else edge
        obs_adj = 0
        if obstacles:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        obs_adj += 1
        return (d if is_evader else -d) + 0.15 * edge_bias - 0.5 * obs_adj

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v = score(nx, ny)
        if best_val is None or v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]