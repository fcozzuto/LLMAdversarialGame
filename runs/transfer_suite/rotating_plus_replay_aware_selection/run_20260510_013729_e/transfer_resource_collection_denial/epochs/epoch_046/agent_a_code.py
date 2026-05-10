def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    res_set = {(x, y) for x, y in resources}
    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_move = [0, 0]
    best_key = None

    # If already on a resource, collect it deterministically by staying unless blocked (staying is allowed).
    if (sx, sy) in res_set:
        return [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        if (nx, ny) in obst:
            # Avoid stepping into obstacles; the engine would keep us, so treat as staying.
            nx, ny, dx, dy = sx, sy, 0, 0

        my_best_dist = None
        opp_best_dist = None
        cap = 0

        # Choose the resource that this candidate would prioritize: maximize lead and arrival tempo.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if my_best_dist is None or (ds, -do, (rx, ry)) < (my_best_dist, -opp_best_dist, (chosen_rx, chosen_ry)):
                my_best_dist, opp_best_dist = ds, do
                chosen_rx, chosen_ry = rx, ry
            # cap if directly landing on any resource (tie-break later)
            if (nx, ny) == (rx, ry):
                cap = 1

        # Lead is (opponent distance - my distance): positive means we are closer.
        lead = (opp_best_dist - my_best_dist)

        # Also discourage moving away from "nearest capture" by anchoring on chosen resource.
        # Deterministic tie-break by resource ordering.
        key = (
            cap,
            lead,
            -my_best_dist,
            -opp_best_dist,
            -(chosen_rx * 8 + chosen_ry),
            (dx, dy),
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move