def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_to_opp(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    target = None
    bestd = 10**9
    for ux, uy in unclaimed:
        if adj_to_opp(ux, uy):
            d = dist(x, y, ux, uy)
            if d < bestd:
                bestd = d
                target = (ux, uy)
    if target is None and unclaimed:
        for ux, uy in unclaimed:
            d = dist(x, y, ux, uy)
            if d < bestd:
                bestd = d
                target = (ux, uy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 1000
        if (nx, ny) in unclaimed:
            score += 20 if adj_to_opp(nx, ny) else 8
        for adx, ady in neigh4:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in selfT:
                score += 3
        if target is not None:
            score -= dist(nx, ny, target[0], target[1]) * 0.8

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]