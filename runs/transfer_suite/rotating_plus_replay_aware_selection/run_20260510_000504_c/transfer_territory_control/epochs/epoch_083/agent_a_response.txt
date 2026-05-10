def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    # Resource: prefer it but still use safety/territory heuristics.
    res_target = resources[0] if resources else None

    best = None
    best_g = -10**18

    def min_dist_to_unclaimed(x, y):
        if not unclaimed:
            return 0
        md = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if d < md:
                md = d
        return md

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        gain = 0.0
        if (nx, ny) in opp_terr:
            gain += 6.0
        elif (nx, ny) in unclaimed:
            gain += 3.0
        elif (nx, ny) in self_terr:
            gain += 1.0

        # Avoid stepping near opponent territory to reduce immediate counterclaim.
        adj_opp = 0
        for ax, ay in neigh:
            if (nx + ax, ny + ay) in opp_terr:
                adj_opp += 1
        if adj_opp:
            gain -= 1.5 * adj_opp

        # Prefer staying away from opponent while expanding.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        gain += 0.12 * dist_opp

        # Resource pull (if present), otherwise expand toward unclaimed.
        if res_target:
            tx, ty = res_target
            gain += -0.25 * (abs(nx - tx) + abs(ny - ty))
        else:
            gain += -0.05 * min_dist_to_unclaimed(nx, ny)

        if gain > best_g:
            best_g = gain
            best = [dx, dy]

    return best if best is not None else [0, 0]