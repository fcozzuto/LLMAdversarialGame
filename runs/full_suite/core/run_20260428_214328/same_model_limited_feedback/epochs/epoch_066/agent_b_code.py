def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Pick a resource to contest based on who is closer (tie-break deterministically).
    best = None
    best_val = -10**9
    for r in resources:
        sd = cd((sx, sy), r)
        od = cd((ox, oy), r)
        # Positive means we are closer (good); also favor nearer resources.
        val = (od - sd) * 100 - sd
        if best is None or val > best_val or (val == best_val and (r[0], r[1]) < best):
            best_val = val
            best = r
    tx, ty = best

    # Deterministically evaluate next moves.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]
    moves.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-break

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_dist = cd((nx, ny), (tx, ty))

        # Discourage stepping closer to opponent (avoid collisions/contesting chaos).
        opp_dist = cd((nx, ny), (ox, oy))
        # Encourage moving toward target.
        score = -self_dist * 100 + opp_dist

        # Extra: if target is also where opponent could be, prefer increasing separation.
        if cd((ox, oy), (tx, ty)) <= cd((sx, sy), (tx, ty)):
            score += opp_dist * 2

        # Favor center a bit to reduce cornering traps.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.05

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]