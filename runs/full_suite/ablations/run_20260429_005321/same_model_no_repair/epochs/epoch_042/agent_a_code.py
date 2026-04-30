def choose_move(observation):
    sx, sy = observation["self_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_adj_pen(x, y):
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            score = -10**9
        else:
            if resources:
                dmin = 10**9
                for rx, ry in resources:
                    d = king_dist(nx, ny, rx, ry)
                    if d < dmin:
                        dmin = d
                score = -dmin
                if (nx, ny) in set((r[0], r[1]) for r in resources):
                    score += 10**6
            else:
                # No visible resources: drift toward opponent corner
                ox, oy = observation["opponent_position"]
                d = king_dist(nx, ny, ox, oy)
                score = -d
            score -= 5 * obs_adj_pen(nx, ny)
            score -= 0.2 * (min(nx, gw - 1 - nx) + min(ny, gh - 1 - ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mx, my]

    return best_move