def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None

    # New policy: target resources where we can beat the opponent by distance,
    # and if hard to beat, still move toward the resource that least favors them.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we can step onto a resource now, do it (strongest deterministic tie-break).
        if (nx, ny) in resources:
            return [dx, dy]

        our_to = []
        opp_to = []
        for rx, ry in resources:
            d_our = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            our_to.append(d_our)
            opp_to.append(d_opp)

        # Choose the resource giving best "win margin" (opp_dist - our_dist).
        # Higher is better. Add slight penalty for long travel and being close to opponent.
        best_margin = None
        best_for = None
        for i, (rx, ry) in enumerate(resources):
            d_our = our_to[i]
            d_opp = opp_to[i]
            margin = d_opp - d_our
            if best_margin is None or margin > best_margin or (margin == best_margin and d_our < dist(nx, ny, resources[best_for][0], resources[best_for][1])):
                best_margin = margin
                best_for = i

        d_our_sel = our_to[best_for]
        d_opp_sel = opp_to[best_for]
        d_op_now = dist(nx, ny, ox, oy)

        # Encourage beating opponent (margin), but also prevent getting trapped by huge distances.
        score = (best_margin * 100) - (d_our_sel * 3) + (d_opp_sel == d_our_sel) * 1 - (d_op_now == 0) * 50
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]