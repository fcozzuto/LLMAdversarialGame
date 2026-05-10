def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp_pos = observation.get("opponent_position", None)
    ox, oy = opp_pos if (isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2) else (-999, -999)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(x + dx, y + dy, dx, dy) for dx, dy in deltas if inb(x + dx, y + dy)]
    if not moves:
        return [0, 0]

    def edge_dist(cx, cy):
        return min(cx, w - 1 - cx, cy, h - 1 - cy)

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def risk(nx, ny):
        r = 0
        for dx2, dy2 in neigh:
            px, py = nx + dx2, ny + dy2
            if (px, py) in oppT:
                r += 3
            if (px, py) in obstacles:
                r += 1
        # also penalize being near opponent position
        if ox != -999:
            d = abs(nx - ox) + abs(ny - oy)
            if d == 0:
                r += 20
            elif d <= 2:
                r += 8
            elif d <= 4:
                r += 3
        return r

    best = None
    for nx, ny, dx, dy in moves:
        if (nx, ny) in obstacles:
            continue
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 16
        if (nx, ny) in oppT:
            gain += 10
        if (nx, ny) in selfT:
            gain += 2
        # Prefer expanding toward board edges while staying safe from opponent counterclaims
        gain += (w + h - 2 * edge_dist(nx, ny)) * 0.25
        gain -= risk(nx, ny) * 1.0
        # Slight preference to avoid immediate stagnation when unclaimed exist
        if unclaimed:
            gain -= 0.02 * (abs(nx - x) + abs(ny - y) == 0)
        # Deterministic tie-break: lowest ( -gain, dx, dy, nx, ny ) via consistent compare
        key = (-gain, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]