def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer expanding from our frontier; otherwise go to nearest valuable cell.
    frontier = []
    for x, y in self_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in (unclaimed | opp_terr | resources):
                    frontier.append((nx, ny))
    if not frontier:
        candidates = list((unclaimed | opp_terr | resources) or {(w - 1, h - 1)})
    else:
        candidates = list(set(frontier))

    tx, ty = candidates[0]
    for cx, cy in candidates[1:]:
        d = abs(cx - sx) + abs(cy - sy)
        bd = abs(tx - sx) + abs(ty - sy)
        if d < bd or (d == bd and (cy < ty or (cy == ty and cx < tx))):
            tx, ty = cx, cy

    def cell_pref(px, py):
        if (px, py) in opp_terr:
            return 20
        if (px, py) in resources:
            return 12
        if (px, py) in unclaimed:
            return 9
        if (px, py) in self_terr:
            return 4
        return 1

    # Evaluate one-step moves with local adjacency pressure.
    best = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    ex, ey = nx + ax, ny + ay
                    if inb(ex, ey) and ((ex, ey) in (unclaimed | opp_terr | resources)):
                        adj += 1
            dist = abs(nx - tx) + abs(ny - ty)
            # Higher is better; add deterministic tie-break.
            sc = cell_pref(nx, ny) + adj * 2 - dist
            key = (sc, -nx, -ny, dx, dy)
            if best is None or key > best:
                best = key
                best_move = [dx, dy]

    # If all moves blocked, stay.
    if best is None:
        return [0, 0]
    return best_move