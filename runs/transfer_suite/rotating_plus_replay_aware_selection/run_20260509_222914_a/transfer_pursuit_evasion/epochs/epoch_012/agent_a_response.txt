def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h and (a, b) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners = [c for c in corners if inb(c[0], c[1])] or [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    # Prefer moving toward the corner farthest from the opponent, but always maximize separation locally.
    target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        d_now = cheb(x, y, ox, oy)
        d_new = cheb(nx, ny, ox, oy)

        # Separation is primary; corner direction is secondary; avoid "trap" moves that reduce separation.
        corner_dx = 0 if target[0] == nx else (1 if target[0] > nx else -1)
        corner_dy = 0 if target[1] == ny else (1 if target[1] > ny else -1)
        dir_match = 1 if (corner_dx == dx and corner_dy == dy) else 0

        # Obstacle penalty: discourage moves that have fewer free exits.
        free_exits = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                free_exits += 1

        score = (
            1000 * (d_new - d_now) +
            50 * d_new +
            8 * dir_match +
            0.5 * free_exits
        )
        # Hard discourage stepping closer than current unless no other options.
        if d_new < d_now:
            score -= 200

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]