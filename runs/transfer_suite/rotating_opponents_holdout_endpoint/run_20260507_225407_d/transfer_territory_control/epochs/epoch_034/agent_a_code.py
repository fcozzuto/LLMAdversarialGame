def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Targeting: nearest unclaimed generally, but also sometimes cut into opponent territory.
    un_list = list(un)
    if un_list:
        # Deterministic choice: minimize (dist to us - 0.6*dist to opp) then tie-break by index
        best_u = None
        for i, (x, y) in enumerate(un_list):
            val = man(x, y, sx, sy) - 0.6 * man(x, y, ox, oy) + 0.001 * (x * 8 + y)
            if best_u is None or val < best_u[0]:
                best_u = (val, x, y)
        tx, ty = best_u[1], best_u[2]
    else:
        # If no unclaimed, bias towards nearest opponent territory cell to attack.
        opp_list = list(opp_t) if opp_t else [(ox, oy)]
        best_o = None
        for i, (x, y) in enumerate(opp_list):
            val = 1.2 * man(x, y, sx, sy) + 0.001 * (x * 8 + y) + 0.02 * man(x, y, ox, oy)
            if best_o is None or val < best_o[0]:
                best_o = (val, x, y)
        tx, ty = best_o[1], best_o[2]

    # Evaluate immediate moves.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        # Prefer claiming/attacking frontier cells.
        if (nx, ny) in un:
            score += 9.0
        if (nx, ny) in opp_t:
            score += 7.0
        if (nx, ny) in self_t:
            score += 1.0

        # Progress toward target.
        score += 0.15 * (man(tx, ty, ox, oy) - man(nx, ny, ox, oy))
        score += -0.6 * man(nx, ny, tx, ty)

        # Slightly avoid giving opponent immediate access: move away if landing on/adjacent to their position.
        score += -0.3 * man(nx, ny, ox, oy)

        # Small deterministic tie-break.
        score += 0.0001 * (nx * 8 + ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move