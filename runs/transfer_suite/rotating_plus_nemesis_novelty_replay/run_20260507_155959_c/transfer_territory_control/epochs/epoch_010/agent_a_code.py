def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_list = list(opp_cells) if opp_cells else [(ox, oy)]
    def min_dist_to_opp(x, y):
        px, py = x, y
        md = 10**9
        for tx, ty in opp_list:
            d = abs(tx - px) + abs(ty - py)
            if d < md:
                md = d
        return md

    # Pick a deterministic target among unclaimed cells: far from opponent but not too far from us.
    target = None
    if unclaimed:
        best = None
        for x, y in unclaimed:
            if (x, y) in obstacles or not inb(x, y):
                continue
            d_ou = man((x, y), (sx, sy))
            d_op = min_dist_to_opp(x, y)
            # prefer cells that we can reach reasonably while keeping distance from opponent
            k = (-(d_op), d_ou, x, y)
            if best is None or k < best:
                best = k
                target = (x, y)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0.0

        if cell in opp_cells:
            score += 6.0  # flipping on entry is enabled
        if cell in self_cells:
            score += 1.5

        if unclaimed:
            if cell in set(unclaimed):
                score += 3.0

        if target is not None:
            # move toward target while preferring to avoid landing near opponent unless capturing
            score += -0.35 * man(cell, target)
            score += 0.12 * min_dist_to_opp(nx, ny)

        # deterministic tie-break: lexicographic on (score, nx, ny)
        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]