def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_opponent_step(px, py, target_x, target_y):
        # Predict evader: choose move that maximizes distance to pursuer (our position).
        best = None
        bestd = -1
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d = man(nx, ny, target_x, target_y)
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return best if best is not None else (0, 0)

    # Our move candidates: aim to minimize distance to predicted opponent next position.
    opp_step = best_opponent_step(ox, oy, sx, sy)
    pred_ox, pred_oy = ox + opp_step[0], oy + opp_step[1]

    best = (0, 0)
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = man(nx, ny, pred_ox, pred_oy)
        if d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)

    return [int(best[0]), int(best[1])]