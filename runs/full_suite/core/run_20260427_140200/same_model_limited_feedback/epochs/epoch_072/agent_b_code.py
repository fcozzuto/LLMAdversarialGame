def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick resource where we have the largest advantage (closer than opponent)
    best = None
    best_adv = -10**9
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        # tie-break toward nearer self
        if adv > best_adv or (adv == best_adv and sd < best[0]):
            best_adv = adv
            best = (sd, rx, ry)

    _, tx, ty = best

    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Candidate moves: primary step toward target, then alternatives
    cand = []
    cand.append((dx, dy))
    # Deterministic alternative ordering: try diagonal variations, then straight, then stay
    alts = [(-dx, dy), (dx, -dy), (dx, 0), (0, dy), (0, 0), (-dx, -dy), (-dx, 0), (0, -dy)]
    for a in alts:
        if a not in cand:
            cand.append(a)

    # Evaluate candidates by: valid, then minimize distance to target; slight penalty if near opponent
    best_move = (0, 0)
    best_score = 10**18
    for mdx, mdy in cand[:9]:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        score = nd * 10 - od  # closer to target, farther from opponent
        if score < best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]