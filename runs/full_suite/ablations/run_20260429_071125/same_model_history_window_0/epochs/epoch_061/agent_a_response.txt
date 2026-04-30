def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        dx = 0 if ox >= sx else 1
        dy = 0 if oy >= sy else 1
        return [dx if dx in (-1, 0, 1) else 0, dy if dy in (-1, 0, 1) else 0]

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Choose target: nearest resource; tie-break by favoring resources closer to us than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        k = (cheb(sx, sy, rx, ry), cheb(ox, oy, rx, ry), rx, ry)
        if best is None or k < best_key:
            best = (rx, ry)
            best_key = k
    tx, ty = best

    # Candidate moves: step toward target, with deterministic tie-breaks; avoid obstacles.
    moves = []
    primary_dx = 0 if tx == sx else (1 if tx > sx else -1)
    primary_dy = 0 if ty == sy else (1 if ty > sy else -1)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                opp_dist = cheb(nx, ny, ox, oy)
                align = -(abs(dx - primary_dx) + abs(dy - primary_dy))
                moves.append((dist, -opp_dist, -align, nx - sx, ny - sy))
    # If all moves invalid, allow staying still or any non-obstacle in bounds.
    if not moves:
        if 0 <= sx < w and 0 <= sy < h and (sx, sy) not in obstacles:
            return [0, 0]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]

    moves.sort()
    dx, dy = moves[0][3], moves[0][4]

    # If best move is not actually moving toward the chosen target (due to obstacle traps), try staying.
    if cheb(sx + dx, sy + dy, tx, ty) >= cheb(sx, sy, tx, ty):
        return [0, 0]
    return [dx, dy]