def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            return int(p[0]), int(p[1])
        return None

    unclaimed = [norm_pos(p) for p in (observation.get("unclaimed_cells") or [])]
    unclaimed = [p for p in unclaimed if p is not None and p not in obstacles]
    myT = set(norm_pos(p) for p in (observation.get("self_territory") or []) if norm_pos(p) is not None)
    oppT = set(norm_pos(p) for p in (observation.get("opponent_territory") or []) if norm_pos(p) is not None)
    unclaimed_set = set(unclaimed)

    in_bounds = lambda x, y: 0 <= x < w and 0 <= y < h
    targets = unclaimed if unclaimed else [p for p in oppT if p not in obstacles]
    if not targets:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**18
    opp_adj = oppT

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        dmin = 10**9
        for t in targets:
            d = abs(t[0] - nx) + abs(t[1] - ny)
            if d < dmin:
                dmin = d

        score = 0
        if cell in opp_adj:
            score += 5.0
        if cell in unclaimed_set:
            score += 2.0
        if cell in myT:
            score -= 0.2

        # Prefer reducing distance to target; tie-break deterministically
        score += (-0.15 * dmin) + (0.02 * (man((sx, sy), min(targets, key=lambda t: man(t, (sx, sy)))) - dmin))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]