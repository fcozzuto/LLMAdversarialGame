def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def adj_has_terr(x, y, terr):
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in terr:
                return True
        return False

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
    if not unclaimed:
        return [0, 0]

    # Deterministic scoring:
    # primary: adjacent to opponent territory (steal/contested edge)
    # secondary: adjacent to our territory (safe expansion)
    # tertiary: distance; then prefer forward direction (roughly toward opposite corner)
    opp_bias = (w - 1 - sx, h - 1 - sy)
    best = None
    best_key = None
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        steal = 1 if adj_has_terr(x, y, opp_terr) else 0
        expand = 1 if adj_has_terr(x, y, self_terr) else 0
        dist = abs(x - sx) + abs(y - sy)
        forward = (opp_bias[0] * (x - sx) + opp_bias[1] * (y - sy))
        # higher steal/expand, lower dist, higher forward, then lexicographic tie-break
        key = (-(steal * 1000 + expand * 100) + dist, -forward, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # fallback: try one axis move (still deterministic)
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]