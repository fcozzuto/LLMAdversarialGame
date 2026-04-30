def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    move_options = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Default: move towards center to reduce being pinned
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_val = 10**9
        for dx, dy in move_options:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles: 
                continue
            val = abs(nx - tx) + abs(ny - ty)
            if val < best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    alpha = 0.8  # prefer resources opponent is far from
    best_move = [0, 0]
    best_val = 10**18

    for dx, dy in move_options:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            val = 10**12
        else:
            min_score = 10**18
            for rx, ry in resources:
                dist_you = d((nx, ny), (rx, ry))
                dist_opp = d((ox, oy), (rx, ry))
                score = dist_you - alpha * dist_opp
                if score < min_score:
                    min_score = score
            # small tie-breakers: avoid moving closer to opponent when competing
            val = min_score + 0.05 * d((nx, ny), (ox, oy))
        if val < best_val - 1e-9:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]