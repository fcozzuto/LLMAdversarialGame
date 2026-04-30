def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a target resource that we can reach earlier than the opponent (greedy, deterministic)
    if resources:
        best_r = None
        best_val = None
        for r in resources:
            myd = dist((myx, myy), r)
            opd = dist((ox, oy), r)
            # Prefer resources where myd - opd is smallest; tie-break by coordinate order
            val = myd - opd
            if best_val is None or val < best_val or (val == best_val and (r[0], r[1]) < (best_r[0], best_r[1])):
                best_val = val
                best_r = r
        target = best_r
    else:
        # No resources: go toward center while keeping away from opponent
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = myx + dx, myy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue  # avoid stepping into obstacles when possible

        myd_next = dist((nx, ny), target)
        oppd_next = dist((nx, ny), (ox, oy))

        # Tradeoff: get closer to target, and keep distance from opponent (reduces contesting/blocking)
        score = myd_next - 0.35 * oppd_next

        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]