def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    # distance with 8-direction moves (Chebyshev)
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick best target resource
    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # prefer resources we can reach first; otherwise avoid contested ones
        score = ds
        if ds < do:
            score = ds
        else:
            score = ds + (do - ds + 1) * 5
        # mild tie-break toward staying away from opponent
        score += max(0, 2 - dist((ox, oy), (rx, ry))) * 0.2
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # fallback: move toward opponent corner by reducing distance to a random-free heuristic (deterministic)
        tx, ty = (w - 1, 0) if (sx == 0 and sy == h - 1) else (0, h - 1)
    else:
        tx, ty = best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_m = (0, 0)
    best_val = None
    # evaluate next steps deterministically
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = dist((nx, ny), (tx, ty))
        # keep from walking into opponent influence
        dso = dist((nx, ny), (ox, oy))
        # prefer improving toward target; in ties, maximize opponent distance
        val = ds2 * 10 - dso * 0.3 + (0 if (nx, ny) == (tx, ty) else 0.01)
        if best_val is None or val < best_val:
            best_val = val
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]