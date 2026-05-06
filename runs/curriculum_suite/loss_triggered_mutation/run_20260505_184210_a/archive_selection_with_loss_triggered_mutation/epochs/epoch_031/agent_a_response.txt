def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w // 2, h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Consider a small deterministic subset of resources
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # sort by closeness to us, tie by coordinates
    res_sorted = sorted(resources, key=lambda r: (man(r, (sx, sy)), r[0], r[1]))
    res2 = res_sorted[:6]
    # also include best from opponent view to allow contesting
    res_sorted_opp = sorted(resources, key=lambda r: (man(r, (ox, oy)), r[0], r[1]))
    res3 = res_sorted_opp[:3]
    cand_resources = []
    seen = set()
    for r in res2 + res3:
        if r not in seen:
            seen.add(r)
            cand_resources.append(r)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that improve relative position vs opponent on contested resources
        # Add slight penalty for staying too still.
        score = 0.0
        for rx, ry in cand_resources:
            d_self = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)
            # higher means we are closer than opponent (or at least contesting)
            score += (d_opp - d_self)
        # encourage progressing (reduce zero move) deterministically
        score -= 0.15 if (dx == 0 and dy == 0) else 0.0

        # tie-break deterministically by (score, -progress, dx, dy)
        progress = abs(dx) + abs(dy)
        key = (score, progress * 0.01, -dx, -dy)
        if best_score is None or key > best_key:
            best_score = score
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]