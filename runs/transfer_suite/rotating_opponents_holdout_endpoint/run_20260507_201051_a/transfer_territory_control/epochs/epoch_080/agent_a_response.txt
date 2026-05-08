def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    oppT = observation.get("opponent_territory") or []
    opp_set = set((int(p[0]), int(p[1])) for p in oppT if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    frontier = []
    for ux, uy in un_set:
        if any((ux + dx, uy + dy) in opp_set for dx, dy in neigh):
            frontier.append((ux, uy))
    targets = frontier if frontier else (list(un_set) if un_set else [(ox, oy)])

    def score_cell(x, y):
        dtx = x - ox
        dty = y - oy
        away = dtx * dtx + dty * dty
        # Prefer cells near opponent (edge-pressure) and closer to us
        mind = 10**9
        for tx, ty in targets:
            ddx = x - tx
            ddy = y - ty
            v = ddx * ddx + ddy * ddy
            if v < mind:
                mind = v
        return -mind + 0.01 * away

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If moving into opponent territory, strongly encourage (flipping enabled)
        move_val = score_cell(nx, ny)
        if (nx, ny) in opp_set:
            move_val += 10000
        # Softly avoid stepping into positions that are "surrounded" (likely dead-ends)
        blocked = 0
        for ddx, ddy in neigh:
            ax, ay = nx + ddx, ny + ddy
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                blocked += 1
        move_val -= 0.1 * blocked
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]