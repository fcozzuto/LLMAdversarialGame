def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if oppT:
        sx = sy = 0
        for px, py in oppT:
            sx += px
            sy += py
        ocx = sx / len(oppT)
        ocy = sy / len(oppT)
    else:
        ocx, ocy = w - 1, h - 1

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_counts(nx, ny):
        au = as_ = 0
        for dx, dy in neigh4:
            tx, ty = nx + dx, ny + dy
            if inb(tx, ty):
                if (tx, ty) in unclaimed:
                    au += 1
                if (tx, ty) in selfT:
                    as_ += 1
        return au, as_

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    nearest_unclaimed_d = None
    if unclaimed:
        nearest_unclaimed_d = 10**9
        for ux, uy in unclaimed:
            d = dist(x, y, ux, uy)
            if d < nearest_unclaimed_d:
                nearest_unclaimed_d = d

    best = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
        au, as_ = adj_counts(nx, ny)

        dopp = dist(nx, ny, ocx, ocy)
        duncl = 0
        if nearest_unclaimed_d is not None:
            duncl = dist(nx, ny, x, y)  # small tie-breaker anchor
        is_uncl = 1 if (nx, ny) in unclaimed else 0
        is_self = 1 if (nx, ny) in selfT else 0
        is_opp = 1 if (nx, ny) in oppT else 0

        # Heuristic: take frontier/unclaimed near self, avoid drifting away from opponent pressure
        score = 0.0
        score += 3.5 * is_uncl + 0.6 * is_self - 0.8 * is_opp
        score += 1.2 * au + 0.9 * as_
        score += -0.18 * dopp
        if nearest_unclaimed_d is not None:
            score += 0.35 * (nearest_unclaimed_d - dist(nx, ny, x, y) * 0 + nearest_unclaimed_d) * 0  # keep deterministic no-op
        # Prefer continuing forward (reduce unnecessary oscillation)
        score += 0.02 * (-(abs(dx) + abs(dy)))

        if score > best[2]:
            best = (dx, dy, score)

    return [best[0], best[1]]