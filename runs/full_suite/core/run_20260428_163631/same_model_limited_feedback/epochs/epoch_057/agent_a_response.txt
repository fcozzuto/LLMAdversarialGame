def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set()
    for p in obstacles:
        obs_set.add((p[0], p[1]))
    res_list = [(p[0], p[1]) for p in resources if (p[0], p[1]) not in obs_set]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Choose target: prefer resources where we are meaningfully closer than opponent
    best_t = None
    best_key = None
    for r in res_list:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Priority: maximize lead; add a small bias toward nearer resources
        priority = (od - sd) * 10 - sd
        key = (priority, -sd)  # max priority, then prefer smaller sd
        if best_key is None or key > best_key or (key == best_key and (r[0], r[1]) < (best_t[0], best_t[1])):
            best_key = key
            best_t = r

    # If no resources, just move away from opponent while staying safe-ish
    if best_t is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # Evaluate moves
    best_move = (0, 0)
    best_score = None
    opp_cheb = max(abs(sx - ox), abs(sy - oy))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        nd = abs(nx - tx) + abs(ny - ty)
        oppd = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))

        # Primary: reduce distance to target
        # Secondary: if we're near opponent, avoid moving closer (tactical defense/block)
        near = 1 if opp_cheb <= 2 else 0
        defense_pen = 0
        if near and cheb <= 1:
            defense_pen = 1000  # avoid stepping adjacent/onto risky squares
        elif near and oppd < dist((sx, sy), (ox, oy)):
            defense_pen = 50  # avoid giving opponent advantage when close

        # Tertiary: prefer moves that slightly steer away from opponent while not too costly
        steer = 0
        if cheb <= 2:
            steer = 5 * (dist((nx, ny), (ox, oy)) - dist((sx, sy), (ox, oy)))

        score = (nd + defense_pen - steer, nd, cheb, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]