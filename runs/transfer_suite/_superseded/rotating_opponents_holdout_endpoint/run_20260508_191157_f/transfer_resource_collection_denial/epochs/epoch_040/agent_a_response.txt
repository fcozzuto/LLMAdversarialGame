def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # prefer resources where we are closer; tie-break by absolute self distance then coords
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def score(nx, ny):
        hit = (nx, ny) in obs_set
        if hit:
            return -10**9
        myd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - nx) + abs(ty - ny)  # same target, but we use opponent position below
        opp_dist = abs(tx - ox) + abs(ty - oy)
        # encourage advancing and slightly denying (maximize our lead at next step)
        my_now = abs(tx - sx) + abs(ty - sy)
        lead_now = (abs(tx - ox) + abs(ty - oy)) - my_now
        lead_next = (abs(tx - ox) + abs(ty - oy)) - myd
        return (lead_next - myd * 0.01, -myd, -abs(nx - ox) - abs(ny - oy) * 0.001)

    best_move = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    # If all non-stay moves are blocked, at least try staying (allowed)
    if best_move == (0, 0) and (sx, sy) in obs_set:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]