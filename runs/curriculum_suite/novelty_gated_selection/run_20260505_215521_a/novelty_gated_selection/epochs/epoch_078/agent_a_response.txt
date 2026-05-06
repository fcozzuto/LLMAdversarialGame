def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, maximize distance from opponent while staying feasible.
    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            # tiny tie-break toward moving (not staying)
            score = (d * 10) + (0 if (dx == 0 and dy == 0) else 1)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Evaluate each candidate move by targeting resources with "who is closer" competition.
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Threat/targeting: prefer resources where we can arrive sooner than opponent.
        move_score = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # If we can capture immediately, strongly prefer.
            if ds == 0:
                move_score += 10_000
                continue

            # Relative advantage: positive if we are closer (or equal).
            rel = do - ds
            # Encourage taking over the nearest feasible "swing" target.
            move_score += (rel * 120) - (ds * 5)

            # Discourage letting opponent take it first by a large margin.
            if rel < 0:
                move_score += rel * 40  # more negative rel => worse

        # Prefer staying closer to the "frontier" toward resources.
        # (Small tie-break to reduce dithering.)
        if move_score == best[0]:
            if (dx != 0 or dy != 0) and (best[1] == 0 and best[2] == 0):
                best = (move_score, dx, dy)
        elif move_score > best[0]:
            best = (move_score, dx, dy)

    return [best[1], best[2]]