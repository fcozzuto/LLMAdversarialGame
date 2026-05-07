def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    if not resources:
        return [0, 0]

    def best_target(x, y):
        best = None
        for rx, ry in resources:
            sd = (x - rx) * (x - rx) + (y - ry) * (y - ry)
            if best is None or sd < best[0]:
                best = (sd, rx, ry)
        return best[1], best[2]

    tx, ty = best_target(sx, sy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = abs(nx - tx) + abs(ny - ty)
        od = abs(ox - tx) + abs(oy - ty)
        score = (od - sd) * 100 - sd
        for ex, ey in obs:
            d = abs(nx - ex) + abs(ny - ey)
            if d == 0:
                score -= 100000
            elif d == 1:
                score -= 8
            elif d == 2:
                score -= 3
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]