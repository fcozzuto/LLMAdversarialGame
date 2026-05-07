def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    if not resources:
        return [0, 0]

    dirs8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_block(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 2
        return p

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # choose a resource we can reach sooner or tie; prefer largest margin, then closer to us, then deterministic order
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = manh((sx, sy), (rx, ry))
        od = manh((ox, oy), (rx, ry))
        margin = od - sd  # positive means we are earlier
        if best is None:
            best = (margin, -sd, rx, ry, (rx, ry))
        else:
            bm = best[0]
            if margin > bm:
                best = (margin, -sd, rx, ry, (rx, ry))
            elif margin == bm:
                if -sd > best[1]:
                    best = (margin, -sd, rx, ry, (rx, ry))
                elif -sd == best[1]:
                    if (rx, ry) < (best[3], best[2]):
                        pass

    if best is None:
        return [0, 0]
    target = best[4]
    tx, ty = target

    # Evaluate 9 possible moves and pick best one-step action (obstacle-aware, also tries to reduce distance to target and increase opponent distance)
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in [(0, 0)] + dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd1 = manh((nx, ny), (tx, ty))
        od1 = manh((ox, oy), (tx, ty))
        # if we can already secure sooner, push hard; otherwise maximize delay against opponent (increase opponent relative)
        margin = od1 - sd1
        # slight preference to avoid obstacle-adjacent cells
        val = margin * 1000 - sd1 * 3 - cell_block(nx, ny)
        # tie-break deterministically by move direction then position
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move