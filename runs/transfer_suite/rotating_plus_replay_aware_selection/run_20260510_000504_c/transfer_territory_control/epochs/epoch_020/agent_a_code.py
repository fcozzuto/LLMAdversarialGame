def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 1000
        if (nx, ny) in self_terr:
            sc -= 5
        if opp_terr and (nx, ny) in opp_terr:
            sc -= 50

        # Prefer approaching our target cells and not walking into opponent pressure
        d_op = abs(nx - ox) + abs(ny - oy)
        sc += d_op * 2

        # Bonus if near unclaimed / near opponent territory (frontline)
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in unclaimed:
                sc += 120
            if inb(tx, ty) and opp_terr and (tx, ty) in opp_terr:
                sc += 25

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best