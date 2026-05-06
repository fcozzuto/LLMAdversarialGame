def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (None, -10**9, 10**9)  # move, score, tie
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my = (nx, ny)
        # Prefer moves that create/extend a "resource lead" vs opponent, then closeness.
        local_best = -10**9
        local_best_dist = 10**9
        for r in resources:
            ds = dist8(my, r)
            do = dist8((ox, oy), r)
            # Lead is positive if we are closer (or equal).
            lead = do - ds
            # Slightly favor nearer resources to avoid overvaluing far leads.
            score = lead * 100 - ds
            if score > local_best or (score == local_best and ds < local_best_dist) or (score == local_best and ds == local_best_dist and (r[0], r[1]) < local_best_r):
                local_best = score
                local_best_dist = ds
                local_best_r = (r[0], r[1])
        # Secondary: encourage progress toward any resource.
        nearest_from_new = min(dist8(my, r) for r in resources)
        # Tertiary: avoid moving directly away from opponent if lead is not strong.
        away_pen = 0
        if dist8(my, (ox, oy)) > dist8((sx, sy), (ox, oy)):
            away_pen = 1
        final_score = local_best - away_pen * 5
        if final_score > best[1] or (final_score == best[1] and nearest_from_new < best[2]) or (final_score == best[1] and nearest_from_new == best[2] and (dx, dy) < best_move):
            best_move = (dx, dy)
            best = (best_move, final_score, nearest_from_new)

    return [best[0][0], best[0][1]]