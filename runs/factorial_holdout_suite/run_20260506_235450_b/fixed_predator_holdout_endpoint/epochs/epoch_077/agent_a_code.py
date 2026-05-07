def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not resources or not legal:
        return [0, 0]

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    # One-step lookahead: choose move that maximizes expected advantage over best reachable resource.
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer resources where we end up closer than opponent; also break ties by closeness.
        best_here = None
        for x, y in res:
            sd = md(nx, ny, x, y)
            od = md(ox, oy, x, y)
            # Bigger is better: we want (od - sd) positive; penalize long self distance slightly.
            val = (od - sd) * 100 - sd
            # If opponent is already at/near target, strongly prefer taking it immediately.
            if od == 0 and sd > 0:
                val -= 100000
            if sd == 0 and od > 0:
                val += 100000
            if best_here is None or val > best_here:
                best_here = val
        # Deterministic tie-break: prefer lexicographically smaller move deltas.
        if best_val is None or best_here > best_val or (best_here == best_val and (dx, dy) < best_move):
            best_val = best_here
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]