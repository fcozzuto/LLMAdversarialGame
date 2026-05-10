def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    best_dxdy = (0, 0)
    best_sc = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        cell = (nx, ny)

        base = 0
        if cell in unclaimed:
            base += 4
        if cell in self_ter:
            base -= 1
        if cell in opp_ter:
            base += 2
        base -= 1.5 * adj_opp
        base += 2.5 * adj_self

        ds = abs(nx - x) + abs(ny - y)
        do = abs(nx - ox) + abs(ny - oy)
        reach_adv = (do - ds)  # positive if we are closer/equal next
        base += 0.5 * reach_adv

        score = base
        if best_sc is None or score > best_sc:
            best_sc = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]