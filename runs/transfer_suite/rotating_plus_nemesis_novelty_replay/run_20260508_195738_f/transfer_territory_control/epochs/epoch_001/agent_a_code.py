def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        obstacles.add((a[0], a[1]))

    unclaimed = set((c[0], c[1]) for c in (observation.get("unclaimed_cells", []) or []))

    self_cells = observation.get("self_territory", None)
    if self_cells is None:
        self_cells = set()
    else:
        self_cells = set((c[0], c[1]) for c in self_cells)

    opp_cells = observation.get("opponent_territory", None)
    if opp_cells is None:
        opp_cells = set()
    else:
        opp_cells = set((c[0], c[1]) for c in opp_cells)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_sc = -10**18

    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda c: cheb(x, y, c[0], c[1]))
    elif opp_cells:
        target = min(opp_cells, key=lambda c: cheb(x, y, c[0], c[1]))
    else:
        target = (ox, oy)

    tx, ty = target if target is not None else (ox, oy)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            sc = -cheb(nx, ny, tx, ty)
            if (nx, ny) in opp_cells:
                sc += 5000
            if (nx, ny) in unclaimed:
                sc += 2000
            if (nx, ny) in self_cells:
                sc += 300
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]