def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    def best_for_pos(px, py):
        best = None
        bestd = None
        for rx, ry in resources:
            d = dist(px, py, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        return best, bestd

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10_000
        else:
            target, d_self = best_for_pos(nx, ny)
            if target is None:
                score = -1000
            else:
                rx, ry = target
                d_opp = dist(ox, oy, rx, ry)
                collect_bonus = 500 if (nx, ny) == (rx, ry) else 0
                score = -d_self * 10 + collect_bonus
                if d_self < d_opp:
                    score += 50
                elif d_self == d_opp:
                    score += 10
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]