def choose_move(observation):
    W, H = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def mdist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def dist(a, b): return (a[0]-b[0])**2 + (a[1]-b[1])**2

    opp = (ox, oy)
    selfp = (sx, sy)

    if not resources:
        best = (0, 0); bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            v = mdist((nx, ny), opp)
            if v > bestv: bestv = v; best = [dx, dy]
        return best

    best_res = resources[0]
    best_gain = -10**9
    for r in resources:
        if (r[0], r[1]) in obstacles: continue
        ds = mdist((sx, sy), r)
        do = mdist(opp, r)
        gain = (do - ds) - 0.01 * dist((sx, sy), r)
        # encourage grabbing resources where we're not slower
        if do >= ds: gain += 0.5
        if gain > best_gain:
            best_gain = gain
            best_res = r

    rx, ry = best_res
    target = (rx, ry)

    # if opponent is very close to a resource, prioritize escaping/contesting instead of greedy nearest
    opp_close = min((mdist(opp, r) for r in resources if (r[0], r[1]) not in obstacles), default=999)
    contest = opp_close <= 2

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: 
            continue
        np = (nx, ny)
        d_to_target = mdist(np, target)
        d_to_opp = mdist(np, opp)

        # prefer moves that get closer to a resource we can contest
        val = -d_to_target + 0.25 * d_to_opp

        # discourage walking into opponent proximity when contesting
        if contest:
            val -= 1.0 / (1 + d_to_opp)

        # slight preference for blocking paths: reduce opponent's distance to nearest resource
        if resources:
            nearest_opp_res = min((mdist(opp, r) for r in resources if (r[0], r[1]) not in obstacles), default=999)
            nearest_opp_after = min((mdist((ox, oy), r) for r in resources if (r[0], r[1]) not in obstacles), default=nearest_opp_res)
            val += 0.05 * (nearest_opp_res - nearest_opp_after)

        # tie-break: keep inside and deterministic toward target direction
        if d_to_target == 0:
            val += 1000
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move