def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are likely to arrive first; if tied, grab nearer ones.
        lead = opd - myd
        # Secondary: avoid resources far behind us in "y progress" to reduce dithering.
        back_pen = (ry - sy) if sy <= 3 else (sy - ry)
        key = (-lead, myd + 0.05 * back_pen, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    # Move: try direct step minimizing distance to target, but avoid obstacles.
    bestm = None
    bestdist = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # Add a small anti-collision bias: don't step into squares very close to opponent.
        od = abs(ox - nx) + abs(oy - ny)
        score = (d, -od)
        if bestdist is None or score < bestdist:
            bestdist = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[0], bestm[1]]