def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Immediate capture if possible
    best_capture = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_set:
            # prefer closer to opponent and closer to our position
            sc = -man(nx, ny, ox, oy) - man(sx, sy, nx, ny)
            if best_capture is None or sc > best_capture[0]:
                best_capture = (sc, dx, dy)
    if best_capture is not None:
        return [int(best_capture[1]), int(best_capture[2])]

    # Choose a frontier-ish target: nearest unclaimed biased toward opponent side
    target = (ox, oy)
    if unclaimed:
        tx0, ty0 = ox, oy
        # Bias point towards opponent corner
        bias_x = tx0
        bias_y = ty0
        best = None
        for tx, ty in unclaimed:
            d1 = man(sx, sy, tx, ty)
            d2 = man(tx, ty, bias_x, bias_y)
            # smaller is better; prefer closer first, then more forward (toward opponent)
            sc = d1 * 1000 - d2
            if best is None or sc < best:
                best = sc
                target = (tx, ty)

    # Evaluate moves by projected distance to target and slight preference for growing towards opponent
    bestv = None
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, target[0], target[1])
        d_to_opp = man(nx, ny, ox, oy)
        # tie-break: prefer staying within bounds and reduce oscillation by preferring non-diagonal only if equal
        diag = 1 if dx != 0 and dy != 0 else 0
        val = d_to_t * 10 + d_to_opp - diag
        if bestv is None or val < bestv:
            bestv = val
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]