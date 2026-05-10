def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer a cell adjacent to opponent (likely contest/pressure), else nearest resource, else center.
    opp_adj = []
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
        x, y = ox + dx, oy + dy
        if inb(x, y) and (x, y) not in obstacles:
            opp_adj.append((x, y))
    if opp_adj:
        tx, ty = min(opp_adj, key=lambda p: (man(sx, sy, p[0], p[1]), man(ox, oy, p[0], p[1]), p[0], p[1]))
    else:
        resources = observation.get("resources") or []
        res_cells = []
        for p in resources:
            if not p:
                continue
            x, y = p
            if inb(x, y) and (x, y) not in obstacles:
                res_cells.append((x, y))
        if res_cells:
            # Prefer resources closest to us.
            tx, ty = min(res_cells, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            tx, ty = (w // 2, h // 2)

    best = (10**9, 10**9, 0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: move closer to target. Secondary: don't give opponent a closer approach.
        score = man(nx, ny, tx, ty)
        opp_score = man(ox, oy, nx, ny)
        cand_key = (score, -opp_score, dx, dy)
        if cand_key < (best[0], best[1], best[2], best[3]):
            best = (score, -opp_score, dx, dy)

    if best[2] == 0 and best[3] == 0:
        # If no move was possible except staying, ensure we return a valid direction.
        return [0, 0]
    return [int(best[2]), int(best[3])]