def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                unclaimed.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for (x, y) in unclaimed:
        our_d = man(sx, sy, x, y)
        opp_d = man(ox, oy, x, y)
        center_dist = abs(x - cx) + abs(y - cy)  # prefer interior (smaller)
        edge_pen = 0
        if x in (0, w - 1) or y in (0, h - 1):
            edge_pen = 6  # avoid edge rushing; opponent archetype does that
        score = (opp_d - our_d) * 10 - our_d - 1.5 * center_dist - edge_pen
        key = (-score, our_d, x, y)  # deterministic tie-break: smaller our_d, then coords
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        tx, ty = int(round(cx)), int(round(cy))
    else:
        tx, ty = best

    # move one step toward target, avoiding obstacles if possible
    best_move = [0, 0]
    best_md = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md = (abs(nx - tx) + abs(ny - ty)) * 10 + (abs(nx - ox) + abs(ny - oy))
        if best_md is None or md < best_md or (md == best_md and (dx, dy) < (best_move[0], best_move[1])):
            best_md = md
            best_move = [dx, dy]

    if best_md is None:
        return [0, 0]
    return best_move