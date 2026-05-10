def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obst = set(tuple(p) for p in obstacles)
    resources = observation.get("resources") or []
    rem = observation.get("remaining_resource_count", None)
    self_ter = observation.get("self_territory") or []
    opp_ter = observation.get("opponent_territory") or []

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cur_dop = man((sx, sy), (ox, oy))

    if resources and (rem is None or rem > 0):
        targets = [tuple(p) for p in resources]
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
                continue
            tr = min(man((nx, ny), t) for t in targets)
            dop = man((nx, ny), (ox, oy))
            v = -tr - 0.2 * dop
            if best is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    selfset = set(tuple(p) for p in self_ter)
    oppset = set(tuple(p) for p in opp_ter)

    # Prefer expanding into unoccupied territory near boundary; otherwise chase opponent deterministically.
    unclaimed = observation.get("unclaimed_cells") or []
    targets = [tuple(p) for p in unclaimed] if unclaimed else list(oppset) if oppset else [(ox, oy)]
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue
        d = min(man((nx, ny), t) for t in targets)
        on_self = (nx, ny) in selfset
        in_opp = (nx, ny) in oppset
        dop = man((nx, ny), (ox, oy))
        v = -d
        if not on_self: v += 1.0
        if in_opp: v += 5.0
        # avoid getting too close to opponent
        v -= 0.3 * max(0, (cur_dop - dop))
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return list(best) if best is not None else [0, 0]