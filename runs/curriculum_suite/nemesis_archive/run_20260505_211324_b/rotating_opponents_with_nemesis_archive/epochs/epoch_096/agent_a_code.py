def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        dx = 0
        if ox > sx: dx = 1
        elif ox < sx: dx = -1
        dy = 0
        if oy > sy: dy = 1
        elif oy < sy: dy = -1
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Target selection is implicit in the value: we prefer resources where we gain tempo over opponent.
        # If opponent is very close to all resources, shift to maximizing distance to keep blocking/avoid collision zones.
        cur_best = -10**18
        total_gain = 0
        for rx, ry in resources:
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            gain = d_op - d_me  # positive means we are closer than opponent
            total_gain += 1 if gain > 0 else 0
            val = gain * 10 - d_me  # prioritize being closer, then nearer
            if val > cur_best:
                cur_best = val

        # Slightly discourage moving adjacent to opponent unless we have a clear winning resource tempo.
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        penalty = 0
        if adj and total_gain <= 1:
            penalty = 5 + md(nx, ny, ox, oy)  # deterministic: small extra cost

        # Also encourage moving towards the "best" resource direction.
        best_val_here = cur_best - penalty + (md(nx, ny, ox, oy) * 0.1)
        if best_val_here > best_val:
            best_val = best_val_here
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]