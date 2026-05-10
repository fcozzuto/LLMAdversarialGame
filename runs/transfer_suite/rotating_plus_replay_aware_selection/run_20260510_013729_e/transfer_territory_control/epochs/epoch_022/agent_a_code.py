def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    if not w or not h:
        return [0, 0]
    x, y = sp[0], sp[1]
    ox, oy = op[0], op[1]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = observation.get("resources", [])
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_resource_dist(nx, ny):
        if not resources:
            return 0
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                d = abs(nx - rx) + abs(ny - ry)
                if best is None or d < best:
                    best = d
        return 0 if best is None else best

    # If we are behind, prioritize moving toward resources; otherwise, prioritize distancing.
    sc_self = observation.get("scores", {}).get("self", observation.get("self_score", 0))
    sc_opp = observation.get("scores", {}).get("opponent", observation.get("opponent_score", 0))
    if sc_self == 0 and sc_opp == 0:
        sc_self = observation.get("self_territory_count", 0)
        sc_opp = observation.get("opponent_territory_count", 0)
    chase = sc_self < sc_opp

    opp_cur_dist = abs(x - ox) + abs(y - oy)
    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        nd_op = abs(nx - ox) + abs(ny - oy)
        nd_res = best_resource_dist(nx, ny)
        if chase:
            # Lower resource distance is better; also keep some separation.
            cand = (-(0 if nd_res is None else nd_res), nd_op)
        else:
            # Higher separation is better; then prefer reducing resource distance.
            cand = (nd_op, -(0 if nd_res is None else nd_res))
        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically.
        tie = (cand[0], cand[1], dx, dy)
        if best is None or tie > best:
            best = tie
    if best is None:
        return [0, 0]
    # Decode chosen dx,dy from stored tie
    dx, dy = best[2], best[3]
    return [int(dx), int(dy)]