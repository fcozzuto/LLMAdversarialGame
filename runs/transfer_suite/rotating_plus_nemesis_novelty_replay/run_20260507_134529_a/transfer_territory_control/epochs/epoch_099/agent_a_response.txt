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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    nb = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nb.append((dx, dy, nx, ny))
    if not nb:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Detect our frontier for expansion pressure
    frontier = set()
    for (tx, ty) in self_terr:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed or (nx, ny) in opp_terr:
                    frontier.add((nx, ny))

    opp_frontier = set()
    for (tx, ty) in opp_terr:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed or (nx, ny) in self_terr:
                    opp_frontier.add((nx, ny))

    # Greedy one-step with deterministic tie-breaking; prefer invasion when it is directly adjacent.
    best = None  # (score, -invade, -front, opp_dist, dx, dy)
    for dx, dy, nx, ny in nb:
        invade = 1 if (nx, ny) in opp_terr else 0
        claim = 1 if (nx, ny) in unclaimed else 0
        ours = 1 if (nx, ny) in self_terr else 0
        base = 0.0
        if invade:
            base += 8.0
        elif claim:
            base += 3.0
        elif ours:
            base += 0.8
        else:
            base += 0.6

        # Resource hook
        if (nx, ny) in resources:
            base += 4.0

        d_opp = man((nx, ny), (ox, oy))
        d_self = man((nx, ny), (sx, sy))  # usually 0/1, breaks ties slightly

        # If we can take adjacent unclaimed on our frontier, do it; otherwise, keep pressure on opponent frontier.
        front = 1 if (nx, ny) in frontier else 0
        opp_front = 1 if (nx, ny) in opp_frontier else 0
        base += (2.2 * front) + (1.2 * opp_front)

        # Avoid walking into likely opponent expansion lanes: slightly prefer larger distance from opponent when not invading.
        if not invade:
            base += 0.15 * d_opp

        # Keep a tiny bias toward moving (prevents stuck loops)
        base -= 0.05 * d_self

        cand = (base, -invade, -front, d_opp, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[4]), int(best[5])]