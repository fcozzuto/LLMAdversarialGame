def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x, y, x2, y2):
        dx = x - x2
        if dx < 0:
            dx = -dx
        dy = y - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    t = int(observation.get("turn_index", 0) or 0)
    corner_target = corners[t % 4]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        # Secondary safety: avoid moves that get "boxed" by nearby obstacles.
        blocked_neighbors = 0
        for ex, ey in moves:
            ax, ay = nx + ex, ny + ey
            if not ok(ax, ay):
                blocked_neighbors += 1

        # Corner influence: for evader, prefer maximizing distance to opponent and heading to a far corner.
        if pursuer:
            # Intercept: minimize distance; prefer lower corner_target distance as a tiebreaker.
            corner_dist = cheb(nx, ny, corner_target[0], corner_target[1])
            score = (-d * 100 - corner_dist - blocked_neighbors * 0.3)
            better = (best_score is None) or (score > best_score)
        else:
            corner_dist = cheb(nx, ny, corner_target[0], corner_target[1])
            opp_corner_dist = cheb(ox, oy, corner_target[0], corner_target[1])
            # Evade: maximize distance; bias toward corner farther from opponent; avoid being boxed.
            score = (d * 100 + (corner_dist - opp_corner_dist) * 1.5 - blocked_neighbors * 0.6)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]