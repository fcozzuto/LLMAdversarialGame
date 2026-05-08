def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Prefer cells adjacent to opponent territory (deny expansion / seize frontier)
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    frontier = set()
    for (x, y) in opp_terr:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    targets = list(frontier) if frontier else list(unclaimed)
    if not targets:
        return [0, 0]
    # Deterministic target choice biased to "toward opponent"
    tx, ty = min(targets, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    def cell_score(nx, ny):
        if (nx, ny) in opp_terr:
            s = 8.0
        elif (nx, ny) in unclaimed:
            s = 4.5
        elif (nx, ny) in resources:
            s = 2.5
        elif (nx, ny) in self_terr:
            s = 1.0
        else:
            s = 0.2
        if (nx, ny) == (tx, ty):
            s += 3.0
        if (nx, ny) in resources:
            s += 2.0
        # Small anti-drift: prefer getting closer to target; slightly prefer keeping distance from opponent
        s += 1.0 * (abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny)))
        s += 0.12 * (abs(ox - nx) + abs(oy - ny))
        return s

    best = (None, -10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = cell_score(nx, ny)
        # tie-break deterministically by delta order preference
        key = (s, -dx * dx - dy * dy, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if key > best[1:]:
            best = ((dx, dy),) + key
    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]