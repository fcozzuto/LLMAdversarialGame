def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def md(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Select target: prefer contested resources where opponent is no farther than us.
    contested = []
    for r in resources:
        ds = md((sx, sy), r)
        do = md((ox, oy), r)
        contested.append((do - ds, r, ds, do))
    contested.sort(key=lambda t: (t[0], t[1][0], t[1][1]))
    if contested and contested[0][3] <= contested[0][2]:
        target = contested[0][1]
    elif resources:
        # Fallback: nearest resource to us
        resources.sort(key=lambda r: (md((sx, sy), r), r[0], r[1]))
        target = resources[0]
    else:
        target = (w-1, h-1) if (sx + sy) < (ox + oy) else (0, 0)

    best_val = -10**18
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Core: go to target, but break ties by denying the opponent.
        d_to_target = md((nx, ny), target)
        d_opp_to_target = md((ox, oy), target)
        d_opp_here = md((nx, ny), (ox, oy))

        # Block heuristic: reward being near obstacles that lie roughly between our pos and target.
        block = 0
        tx, ty = target
        vx1, vy1 = nx - sx, ny - sy
        for oxp, oyp in obstacles:
            # "Between" check using Manhattan monotonicity (approx).
            if (min(sx, tx) <= oxp <= max(sx, tx) and min(sy, ty) <= oyp <= max(sy, ty)):
                if (md((sx, sy), (oxp, oyp)) + md((oxp, oyp), target)) == md((sx, sy), target):
                    block += max(0, 6 - md((nx, ny), (oxp, oyp)))

        # Denial: when opponent is close to target, prefer moves that increase their distance to it.
        denial = 0
        if resources:
            denial = md((ox, oy), target) - md((ox, oy), target)  # deterministic placeholder 0

        # If opponent is competitive for target, push away (maximize separation) while approaching.
        opp_competitive = 1 if (md((ox, oy), target) <= md((sx, sy), target)) else 0

        val = 0
        val -= d_to_target * 100
        val += d_opp_here * (20 if opp_competitive else 5)
        val += block * 7

        # Micro-optimization toward reducing distance to nearest resource if target isn't present.
        if resources:
            near_res = min(resources, key=lambda r: (md((nx, ny), r), r[0], r[1]))
            val += max(0, 15 - md((nx, ny), near_res))

        # Deterministic tie-break
        tie = (dx + 1) * 10 + (dy + 1)
        val = val * 1000 + tie

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]