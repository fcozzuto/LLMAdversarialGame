def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    base = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    if (t + sx + sy) & 1:
        base = base[4:] + base[:4]

    def d2(a, b, x, y):
        dx = a - x
        dy = b - y
        return dx * dx + dy * dy

    # If opponent is far, pursue; if close, prefer resources we can reach earlier.
    closer_weight = 2.5 if (d2(sx, sy, ox, oy) <= 9) else 1.0
    best_score = None
    best_move = [0, 0]

    # Approximate sweep pressure: if opponent is closer to a row/col toward which they likely move,
    # we bias to resources near our intersection with that path via the dist-diff metric.
    for dx, dy in base:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        # Score by best target we can "steal" (reach earlier than opponent), with slight preference for nearer targets.
        local_best = -10**18
        for tx, ty in resources:
            ds = d2(nx, ny, tx, ty)
            do = d2(ox, oy, tx, ty)
            # Bonus if landing on a resource cell.
            on = 1 if (nx == tx and ny == ty) else 0
            # Steal priority: larger dist difference means opponent is farther.
            steal = (do - ds)
            # Penalize long moves from us to reduce dithering.
            move_pen = 0.15 * (ds)
            # Tie-break parity to reduce oscillation: deterministic small bias.
            parity = 0.001 * (((tx + ty + t) & 1) - ((nx + ny) & 1))
            val = closer_weight * steal + 6.0 * on - move_pen + parity
            if val > local_best:
                local_best = val

        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = [dx, dy]
        elif local_best == best_score:
            # Deterministic tie-break: prefer staying still last.
            if best_move == [0, 0] and [dx, dy] != [0, 0]:
                best_move = best_move

    return [int(best_move[0]), int(best_move[1])]