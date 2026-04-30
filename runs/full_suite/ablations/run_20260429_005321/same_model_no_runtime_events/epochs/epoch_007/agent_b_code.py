def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))  # Chebyshev

    opp_legal = []
    for dx, dy in ((i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)):
        nx, ny = ox + dx, oy + dy
        if inside(nx, ny) and (nx, ny) not in obs:
            opp_legal.append((nx, ny))

    self_legal = []
    for dx, dy in ((i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)):
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obs:
            self_legal.append((dx, dy, nx, ny))

    any_res = [r for r in resources if (r[0], r[1]) not in obs]
    if not self_legal:
        return [0, 0]
    if not any_res:
        # Deterministic: head toward center if no resources
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, 0, 0)
        for dx, dy, nx, ny in self_legal:
            key = -dist(nx, ny, cx, cy), -dist(nx, ny, ox, oy), dx, dy
            if key > best:
                best = (*key, dx, dy)
        return [best[-2], best[-1]]

    best_score = -10**18
    best_move = (0, 0)

    # Precompute opponent next-step distances to each resource
    res_list = [(r[0], r[1]) for r in any_res]
    for dx, dy, nx, ny in self_legal:
        move_score = -10**18
        for rx, ry in res_list:
            my_d = dist(nx, ny, rx, ry)
            opp_min = 10**9
            for onx, ony in opp_legal:
                d = dist(onx, ony, rx, ry)
                if d < opp_min:
                    opp_min = d
                    if opp_min == 0:
                        break
            # Prefer being earlier after our move and denying opponent tempo
            s = (opp_min - my_d) * 10 - my_d
            # Tiny deterministic tie-break: prefer resources closer to our side line
            s -= dist(nx, ny, ox, oy) * 0.01
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)
        elif move_score == best_score:
            # Deterministic tie-break
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]