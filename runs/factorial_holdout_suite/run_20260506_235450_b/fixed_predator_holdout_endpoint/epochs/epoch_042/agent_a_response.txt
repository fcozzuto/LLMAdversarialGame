def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Determine whether we currently have "winnable" resources (we can reach strictly sooner)
    self_best_now = 10**9
    opp_best_now = 10**9
    for rx, ry in res:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        if sd < self_best_now:
            self_best_now = sd
        if od < opp_best_now:
            opp_best_now = od

    winnable_exist = False
    for rx, ry in res:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        if sd < od:
            winnable_exist = True
            break

    # Evaluate each legal next step by the best attainable resource after the move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = -10**18
        local_close = 10**18
        for rx, ry in res:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)

            if (nx, ny) == (rx, ry):
                val = 10**9
            else:
                adv = od - sd  # positive means we get there first
                # If we have winnables, strongly prefer positive advantage; otherwise just race closest.
                if winnable_exist:
                    if sd < od:
                        val = adv * 1000 - sd * 2
                    else:
                        val = adv * 200 - sd * 3  # still consider but heavily discounted
                else:
                    val = adv * 100 - sd * 5  # denier opponent still matters

            # Tie-break: smaller distance to the resource
            if sd < local_close or (sd == local_close and val > local_best):
                local_close = sd
            if val > local_best:
                local_best = val

        # Small deterministic bias to keep motion stable: prefer reducing manhattan to the best target estimate
        # (use current best resource under the same scoring view)
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]