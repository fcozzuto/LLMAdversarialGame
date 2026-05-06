def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    blocked = set((p[0], p[1]) for p in obstacles)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
    opp_center_d = abs(ox - cx) + abs(oy - cy)

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            dm = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            if opp_center_d <= 2:
                # Opponent is center-rushing: avoid contested nearby; grab something they can't reach fast.
                # Prefer resources where we are closer AND opponent is sufficiently far.
                score = (do - dm, -dm, abs(rx - cx) + abs(ry - cy))
                # Hard preference for "uncrowded" targets.
                if do >= dm + 2:
                    score = (score[0] + 100, score[1], score[2])
            else:
                # Otherwise, be opportunistic but still deterministic.
                score = (do - dm, -min(dm, 999), abs(rx - cx) + abs(ry - cy))
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dtarget = abs(tx - nx) + abs(ty - ny)
        dcenter = abs(nx - cx) + abs(ny - cy)
        # When opponent is near center, keep pressure by moving away from our corner escape.
        if opp_center_d <= 2:
            key = (-dcenter, -dtarget, dx, dy)
        else:
            key = (-dtarget, dcenter, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]