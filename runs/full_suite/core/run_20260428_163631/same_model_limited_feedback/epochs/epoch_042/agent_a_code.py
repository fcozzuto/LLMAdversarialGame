def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    if not resources:
        moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        dx, dy = 0, 0
        if x < ox: dx = 1
        elif x > ox: dx = -1
        if y < oy: dy = 1
        elif y > oy: dy = -1
        return [dx, dy]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_res = None
    best_gap = -10**9
    for r in resources:
        gap = dist((x, y), r) - dist((ox, oy), r)  # positive means opponent closer
        # prefer being closer: maximize -gap == dist_opp - dist_self
        score = -gap
        if score > best_gap:
            best_gap = score
            best_res = r

    tx, ty = best_res
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= observation["grid_width"] or ny < 0 or ny >= observation["grid_height"]:
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx-tx) + abs(ny-ty)
        opp_d = abs(nx-ox) + abs(ny-oy)
        on_resource = 1 if (nx, ny) in resources else 0
        # avoid letting opponent get too close while pursuing target
        val = (-d) + (5.0 * on_resource) + (0.01 * (opp_d)) + (0.0001 * (dx*dx + dy*dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]