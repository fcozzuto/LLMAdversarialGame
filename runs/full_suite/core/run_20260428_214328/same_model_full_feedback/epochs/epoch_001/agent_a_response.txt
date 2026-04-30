def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def in_bounds(x, y):
        return 0 <= x < observation["grid_width"] and 0 <= y < observation["grid_height"]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-dir

    # If no visible resources, head to center
    if not resources:
        tx, ty = observation["grid_width"] // 2, observation["grid_height"] // 2
    else:
        # Choose resource with best advantage (opp farther than us)
        best = None
        for r in resources:
            dself = dist((sx, sy), r)
            dopp = dist((ox, oy), r)
            # prefer reachable; incorporate slight bias to break ties
            score = (dopp - dself, -dself, r[0], r[1])
            if best is None or score > best[0]:
                best = (score, r)
        tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            nx, ny = sx + mx, sy + my
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_to = dist((nx, ny), (tx, ty))
            # avoid moving "away" if possible; also prefer moves that reduce opponent's access
            d_opp = dist((nx, ny), (ox, oy))
            score = (d_to, -d_opp, nx, ny)
            candidates.append((score, mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3]))
    return [int(candidates[0][1]), int(candidates[0][2])]