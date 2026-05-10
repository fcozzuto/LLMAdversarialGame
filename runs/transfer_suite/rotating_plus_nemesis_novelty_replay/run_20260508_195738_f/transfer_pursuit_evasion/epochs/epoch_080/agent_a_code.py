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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_blocked(x, y):
        return (x, y) in obstacles

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or is_blocked(nx, ny):
            continue
        score = 0
        score -= 2 * (abs(tx - nx) + abs(ty - ny))
        score -= 3 * max(0, 2 - (abs(ox - nx) + abs(oy - ny)))
        if resources:
            score += 5 if (nx, ny) in resources else 0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]