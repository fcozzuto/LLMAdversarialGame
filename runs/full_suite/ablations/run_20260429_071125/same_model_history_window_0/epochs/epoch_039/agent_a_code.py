def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if resources:
            best = None
            best_val = None
            for rx, ry in resources:
                sd = cheb(sx, sy, rx, ry)
                od = cheb(ox, oy, rx, ry)
                val = (sd - od * 0.9, sd, -rx, -ry)
                if best_val is None or val < best_val:
                    best_val = val
                    best = (rx, ry)
            return best
        return (w // 2, h // 2)

    tx, ty = best_target()

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer reaching target, slightly prefer denying (being closer than opponent)
        score = (sd - od * 0.35, sd + (abs(nx - tx) + abs(ny - ty)) * 0.01)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]