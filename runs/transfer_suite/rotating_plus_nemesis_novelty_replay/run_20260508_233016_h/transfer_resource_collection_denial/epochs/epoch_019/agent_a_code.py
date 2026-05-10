def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_step(tx, ty):
        best = None  # (score, dx, dy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            myd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer getting closer and also staying ahead of opponent.
            score = myd - 1.2 * od
            # Avoid giving opponent an immediate capture advantage locally.
            opp_next = man(ox + (1 if ox < nx else (-1 if ox > nx else 0)),
                           oy + (1 if oy < ny else (-1 if oy > ny else 0)), tx, ty)
            score += 0.15 * opp_next
            # Slight preference for moving in direction of target.
            score += 0.02 * (abs(nx - sx) + abs(ny - sy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [0, 0] if best is None else [best[1], best[2]]

    # Pick the resource that maximizes our chance to reach first and sweep lines.
    best = None  # (cost, i)
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Deny opponent when they are on same row/col; also prefer resources nearer to our side.
        row_bonus = 1.35 if ry == oy else 0.0
        col_bonus = 0.75 if rx == ox else 0.0
        # If we can be first soon, it’s strongly preferred.
        first_pressure = 2.0 if sd < od else 0.0
        cost = sd - 1.6 * od - row_bonus - col_bonus - first_pressure
        cand = (cost, i)
        if best is None or cand < best:
            best = cand

    tx, ty = resources[best[1]]
    return best_step(tx, ty)