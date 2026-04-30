def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    opp_dist = cheb((sx, sy), (ox, oy))
    endgame = rem <= 6
    best = None
    best_cost = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        mypos = (nx, ny)

        # Distance to closest remaining resource
        dmin = None
        nearest = None
        for r in resources:
            d = cheb(mypos, r)
            if dmin is None or d < dmin:
                dmin = d
                nearest = r

        # If contesting the same resource line, discourage giving opponent an easy route.
        d_to_opp = cheb(mypos, (ox, oy))
        d_opp_to_near = cheb((ox, oy), nearest) if nearest is not None else opp_dist

        # In endgame, prioritize grabbing a nearby resource; otherwise also keep some distance from opponent.
        if endgame:
            cost = dmin * 10 - (d_opp_to_near - d_to_opp)  # want opponent to be farther from nearest
        else:
            cost = dmin * 10 + max(0, 4 - (d_to_opp)) * 2 - max(0, dmin - 1)  # mild pressure

        # Deterministic tie-break: fixed order by (cost, dx, dy)
        if best_cost is None or cost < best_cost or (cost == best_cost and (dx, dy) < best):
            best_cost = cost
            best = (dx, dy)

    return [int(best[0]), int(best[1])]