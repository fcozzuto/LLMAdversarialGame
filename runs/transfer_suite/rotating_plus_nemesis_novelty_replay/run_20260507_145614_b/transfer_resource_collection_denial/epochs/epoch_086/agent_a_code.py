def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if (sx, sy) in [tuple(r) for r in resources]:
        return [0, 0]

    # Candidate targets: those where opponent is closer; we then intercept by aiming near opponent's next step to that target.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources we can take; otherwise strongly contest opponent-favored ones
        score = (sd - od, sd, abs(rx - (w - 1 - ox)) + abs(ry - (h - 1 - oy)))
        # lower is better for sd-od; but if sd>od we want to contest, so we'll weight by how much od leads
        best_val = (score[0] if sd <= od else score[0] - 2 * (od - sd), score[1], score[2])
        if best is None or best_val < best_val:
            pass
        if best is None or best_val < best[0]:
            best = (best_val, (rx, ry), sd, od)

    (_, (rx, ry), sd, od) = best
    # Decide intercept point if opponent is ahead; else go directly.
    if od < sd:
        # Aim for the cell one step from opponent toward the resource (a local contest point)
        ix = ox + (0 if ox == rx else (1 if rx > ox else -1))
        iy = oy + (0 if oy == ry else (1 if ry > oy else -1))
        target = (ix, iy)
    else:
        target = (rx, ry)

    tx, ty = target
    # Greedy move toward target, but avoid obstacles; tie-break by also reducing opponent distance.
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # keep within board automatically via inside
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
        # prefer collecting soon: if move reaches a resource, heavily prioritize
        on_res = 1 if (nx, ny) in [tuple(r) for r in resources] else 0
        val = (0 if on_res else 1, self_d, opp_d, abs(nx - rx) + abs(ny - ry))
        if bestm is None or val < bestm[0]:
            bestm = (val, dx, dy)
    if bestm is None:
        return [0, 0]
    return [bestm[1], bestm[2]]