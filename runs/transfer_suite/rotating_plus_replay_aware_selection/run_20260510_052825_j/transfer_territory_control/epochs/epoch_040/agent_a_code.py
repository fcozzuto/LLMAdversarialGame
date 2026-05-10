def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_to_set(cx, cy, S):
        for dx, dy in neigh:
            tx, ty = cx + dx, cy + dy
            if (tx, ty) in S:
                return True
        return False

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    best = None
    best_score = -10**9
    # Deterministic tie-break order via neigh list iteration.
    for dx, dy in neigh:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 8
        if (nx, ny) in resources:
            sc += 6
        if adj_to_set(nx, ny, oppT):
            sc += 4
        if adj_to_set(nx, ny, selfT):
            sc += 2
        sc -= man(nx, ny, ox, oy) * 0.2
        sc -= man(nx, ny, x, y) * 0.01
        if sc > best_score:
            best_score = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best