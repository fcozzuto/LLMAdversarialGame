def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # 8-dir steps

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myp = (nx, ny)

        # Evaluate by the best contested resource we can reach sooner than opponent.
        # Also slightly reward increasing separation from opponent (denier counter).
        best_comp = None
        for tx, ty in resources:
            t = (tx, ty)
            ds = dist(myp, t)
            do = dist((ox, oy), t)
            comp = (do - ds, -(ds))  # want maximize (do-ds), then minimize ds
            if best_comp is None or comp > best_comp:
                best_comp = comp

        sep_now = dist((sx, sy), (ox, oy))
        sep_new = dist(myp, (ox, oy))
        sep_bonus = sep_new - sep_now  # discourage getting boxed in

        val = (best_comp[0], best_comp[1], sep_bonus, -dist(myp, (ox, oy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move