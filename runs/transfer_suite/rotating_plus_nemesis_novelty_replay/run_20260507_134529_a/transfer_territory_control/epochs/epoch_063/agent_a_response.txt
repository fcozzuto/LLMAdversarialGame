def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    (sx, sy) = observation.get("self_position", [0, 0])
    (ox, oy) = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    opp = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_neighbors = set()
    for (x, y) in opp:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in opp:
                        opp_neighbors.add((nx, ny))

    # Target: prefer unclaimed near opponent boundary; if none, target opponent-occupied to counterclaim.
    candidates = sorted(list(opp_neighbors & unclaimed))
    if not candidates:
        candidates = sorted(list(opp))
    if not candidates:
        candidates = [(ox, oy)]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                nx, ny = sx + dx, sy + dy
            else:
                nx, ny = sx, sy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Score each move by (1) closeness to best target, (2) entering opponent territory bonus, (3) staying away from opponent position.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        enter_opp = 1 if (nx, ny) in opp else 0
        d_to_target = 10**9
        for tx, ty in candidates:
            d = abs(tx - nx) + abs(ty - ny)
            if d < d_to_target:
                d_to_target = d
        d_opp = abs(ox - nx) + abs(oy - ny)
        # Promote immediate flips, then boundary advance, then reduce opponent proximity.
        score = enter_opp * 1000 - d_to_target * 5 + d_opp * 0.25
        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]