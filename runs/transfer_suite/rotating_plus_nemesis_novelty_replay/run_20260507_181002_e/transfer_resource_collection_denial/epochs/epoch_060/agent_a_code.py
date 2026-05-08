def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(v, d=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return d

    sx, sy = xy(observation.get("self_position", None), (0, 0))
    ox, oy = xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is None:
            continue
        x, y = xy(o, None)
        if x is not None:
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None:
            continue
        x, y = xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = ox, oy
        best_val = -10**9
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -(abs(nx - tx) + abs(ny - ty))
            if v > best_val:
                best_val, best = v, (dx, dy)
        return [best[0], best[1]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Evaluate each move by how much it improves my advantage over the best contestable resource.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Prefer resources where I am closer than opponent; also prefer moving toward them.
        cur_best = -10**18
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            # Advantage: larger is better. Add small tie-break for quick collection.
            val = (op_d - my_d) * 100 - my_d
            if val > cur_best:
                cur_best = val
        # If no advantage yet, still avoid walking away from all resources.
        # Also include slight "stay consistent": bias toward staying in direction of current best resource.
        if cur_best > best_val:
            best_val, best_move = cur_best, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]