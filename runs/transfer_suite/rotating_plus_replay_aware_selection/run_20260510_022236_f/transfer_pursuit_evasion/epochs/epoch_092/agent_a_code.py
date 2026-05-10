def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (sx, sy) == (ox, oy):
        return [0, 0]

    # deterministic tie-break: prefer moves in a fixed order after sorting
    def nearest_obstacle_dist(x, y):
        if not obstacles:
            return 99
        dmin = 99
        for (px, py) in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < dmin:
                dmin = d
        return dmin

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        if is_evader:
            # maximize survival / separation; strongly avoid immediate capture
            if (nx, ny) == (ox, oy):
                score = -10**9
            else:
                score = 8 * dist + 0.7 * nearest_obstacle_dist(nx, ny) - 0.05 * (nx + ny)
        else:
            # pursuer: prioritize capture, then minimize distance; avoid obstacles
            if (nx, ny) == (ox, oy):
                score = 10**9
            else:
                score = -8 * dist + 0.7 * nearest_obstacle_dist(nx, ny) - 0.05 * (nx + ny)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]