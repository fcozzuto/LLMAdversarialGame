def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Filter usable resources
    usable = []
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            usable.append((rx, ry))
    if not usable:
        # No reachable resources (given current obstacles); head toward best open direction
        usable = [(sx, sy)]

    # Pick a target deterministically: closest by Chebyshev distance; tie by lexicographic
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = min(usable, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    tx, ty = target

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Evaluate next-step moves with obstacle avoidance and mild enemy pressure
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    best_move = (0, 0)
    best_score = None

    # Precompute blocked neighbors penalty
    def obstacle_adjacent(x, y):
        p = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Distance to closest resource from the candidate (greedy retargeting)
        dmin = None
        for rx, ry in usable:
            d = cheb(nx, ny, rx, ry)
            if dmin is None or d < dmin:
                dmin = d
        # Mildly prefer moves that also increase distance from opponent
        d_op = cheb(nx, ny, ox, oy)
        # Mildly prefer safer cells
        safe_pen = obstacle_adjacent(nx, ny)
        score = (dmin * 1000) - (d_op * 10) + safe_pen
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]