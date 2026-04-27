def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obs

    if resources:
        best_score = 10**9
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            my_best = 10**9
            their_best = 10**9
            for rx, ry in resources:
                dmy = cheb(nx, ny, rx, ry)
                if dmy < my_best: my_best = dmy
                dto = cheb(ox, oy, rx, ry)
                if dto < their_best: their_best = dto
            score = (my_best - their_best, my_best, abs(dx) + abs(dy))
            if score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_score = 10**9
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        score = (cheb(nx, ny, ox, oy), abs(dx) + abs(dy))
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]