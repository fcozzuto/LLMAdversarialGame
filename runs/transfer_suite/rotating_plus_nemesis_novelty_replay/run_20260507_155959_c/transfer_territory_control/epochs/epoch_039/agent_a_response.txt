def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_cells = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    candidates = []
    for c in unclaimed:
        if c is None or len(c) < 2:
            continue
        x, y = int(c[0]), int(c[1])
        if not inb(x, y) or (x, y) in obstacles:
            continue
        if (x, y) in opp_cells:
            continue
        # Prefer far from opponent, but also not too far from us (balanced)
        dx = abs(x - ox) + abs(y - oy)
        dself = abs(x - sx) + abs(y - sy)
        edge_bonus = (x == 0 or y == 0 or x == w - 1 or y == h - 1)
        score = dx - 0.35 * dself + (0.8 if edge_bonus else 0.0)
        candidates.append((score, x, y))

    if not candidates:
        # Fallback: expand toward farthest non-obstacle neighbor (avoid opponent when possible)
        tx, ty = ox, oy
    else:
        candidates.sort(reverse=True)
        _, tx, ty = candidates[0]

    # Choose best immediate step toward target while keeping away from opponent and obstacles
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If entering opponent territory, be cautious (still allowed by rules); penalize to reduce bad flips
        enter_opp = (nx, ny) in opp_cells
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_t = abs(nx - tx) + abs(ny - ty)
        # Encourage decreasing distance to target and increasing distance from opponent
        v = 1.2 * dist_opp - 0.9 * dist_t - (2.5 if enter_opp else 0.0)
        # Small preference to stay put if all else equal
        if dx == 0 and dy == 0:
            v += 0.05
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best