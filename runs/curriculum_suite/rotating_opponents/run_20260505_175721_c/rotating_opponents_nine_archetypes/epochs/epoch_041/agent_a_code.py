def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Corner-guard response: if opponent is near our side/corner, prioritize winning contested resources.
    # Pick resource that minimizes (myd - opd); i.e., I am closer (negative is best).
    # Tie-break: smaller myd, then deterministic coordinate.
    best = None
    best_key = None
    for tx, ty in resources:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = myd - opd
        key = (adv, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Determine desired direction
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    desired = (sx + dx, sy + dy)

    candidates = []
    for cdx in (-1, 0, 1):
        for cdy in (-1, 0, 1):
            nx, ny = sx + cdx, sy + cdy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # If opponent is close and we can’t win immediately, bias toward center to avoid corner nets.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = 0.0
            dist_opp = man(sx, sy, ox, oy)
            if dist_opp <= 3:
                center_bias = 0.01 * (abs(nx - cx) + abs(ny - cy))
            # Primary: reduce distance to target; secondary: avoid moving away from target.
            score = man(nx, ny, tx, ty) + center_bias + (0.001 * (abs(cdx) + abs(cdy) == 0))
            candidates.append(((score, abs(nx - desired[0]) + abs(ny - desired[1]), cdx, cdy), [cdx, cdy]))

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]