def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dist0 = abs(sx - ox) + abs(sy - oy)

    def min_obstacle_dist(x, y):
        if not obstacles:
            return 10
        md = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        od = min_obstacle_dist(nx, ny)

        # Push for capture when pursuer; push for distancing when evader.
        if evader:
            val = d - 0.25 * (10 - min(od, 10)) - 0.01 * (d < dist0)
            better = best_val is None or val > best_val
        else:
            val = -(1000 * d) + 0.25 * min(od, 10) - 0.01 * (d > dist0)
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]