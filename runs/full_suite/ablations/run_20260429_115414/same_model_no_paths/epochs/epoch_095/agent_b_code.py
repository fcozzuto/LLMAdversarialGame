def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def passable(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic move ordering (slight bias toward reducing x-difference first)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_overall = (10**9, 0, 0)

    def best_target_score(px, py):
        # Higher is better: winning race vs opponent + slight tie-break toward center-ish
        best = -10**18
        for rx, ry in resources:
            dm = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent; avoid giving opponent advantage.
            # Use large weight to create decisive preference.
            score = (do - dm) * 1000 - dm * 3 + (3 - abs(rx - (w - 1) / 2)) + (3 - abs(ry - (h - 1) / 2))
            if score > best:
                best = score
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        score = best_target_score(nx, ny)
        # Deterministic tie-break: prefer moves that also reduce my distance to the best resource
        if score > best_overall[0]:
            best_overall = (score, dx, dy)
        elif score == best_overall[0]:
            # tie-break by minimizing cheb to nearest resource from nx,ny
            mymin = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
            curmin = min(cheb(sx + best_overall[1], sy + best_overall[2], rx, ry) for (rx, ry) in resources)
            if mymin < curmin:
                best_overall = (score, dx, dy)
    return [int(best_overall[1]), int(best_overall[2])]