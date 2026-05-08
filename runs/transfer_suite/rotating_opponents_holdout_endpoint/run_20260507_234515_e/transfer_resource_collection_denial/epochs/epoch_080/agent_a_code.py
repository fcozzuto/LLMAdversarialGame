def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    pref = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Heuristic: prefer resources where we are much closer than opponent.
        cur_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Higher is better: large (od - sd) and smaller sd.
            val = (od - sd) * 10 - sd
            if val > cur_best:
                cur_best = val
        # Secondary: encourage movement toward some resource.
        # If multiple moves lead to same cur_best, pick one with smallest sd to nearest resource.
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]
        elif cur_best == best_val:
            # tie-break deterministically
            nearest_sd_new = min(md(nx, ny, rx, ry) for (rx, ry) in resources)
            nearest_sd_best = min(md(sx + best_move[0], sy + best_move[1], rx, ry) for (rx, ry) in resources)
            if nearest_sd_new < nearest_sd_best:
                best_move = [dx, dy]
    return best_move