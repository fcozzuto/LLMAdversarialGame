def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not targets:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # mild push away from opponent
            score = man((nx, ny), (ox, oy))
            if best is None or score > best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny), dx, dy)
        return [best[2], best[3]] if best else [0, 0]

    # Evaluate each move by the best "advantage" target we can reach relative to opponent.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my = (nx, ny)
        # advantage: opponent is farther than me => positive. Also slightly prefer progress towards that target.
        best_adv = None
        for t in targets:
            md = man(my, t)
            od = man((ox, oy), t)
            adv = (od - md)
            # secondary tie-break: prefer smaller combined distance to encourage commitment
            adv2 = adv * 100 - (md + od)
            if best_adv is None or adv2 > best_adv:
                best_adv = adv2
        if best_score is None or best_adv > best_score or (best_adv == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = best_adv
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]