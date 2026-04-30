def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dxdy = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in dxdy:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def d(a, b, c, e):
        # Chebyshev distance matches diagonal move set
        return max(abs(a - c), abs(b - e))

    # If no resources, head toward opponent to pressure
    if not resources:
        tx, ty = ox, oy
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dxdy:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -d(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
                bestv, best = v, [dx, dy]
        return best

    # Choose move by maximizing advantage on the best contested resource
    best_overall = [0, 0]
    best_score = -10**18

    # Deterministic tie-break order prefers stable/forward-ish moves
    # (diagonals earlier in dxdy list; keep as given)

    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate best resource for us after this move; prefer where we arrive much earlier than opponent
        s_best = -10**18
        for rx, ry in resources:
            sd = d(nx, ny, rx, ry)
            od = d(ox, oy, rx, ry)
            # If we are close and opponent is far, big gain
            # If obstacle forces divergence, still handled by distance and deterministic evaluation
            s = (od - sd) * 10 - sd
            # Mild bias to avoid clustering near opponent late: prefer resources that are closer to us overall
            s -= 0.1 * d(nx, ny, ox, oy)
            if s > s_best:
                s_best = s
        # Small bias to avoid wasting turns (prefer lower distance to chosen best resource indirectly)
        score = s_best
        if score > best_score:
            best_score = score
            best_overall = [dx, dy]
    return best_overall