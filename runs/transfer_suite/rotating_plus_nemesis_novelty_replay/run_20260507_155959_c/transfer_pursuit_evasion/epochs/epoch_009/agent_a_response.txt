def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # escape-option count after move
        nbr = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                nbr += 1

        # target corner opposite to opponent (for evasion), toward/near opponent (for pursuit)
        if pursuer:
            corner_bias = min(nx, w - 1 - nx, ny, h - 1 - ny)  # avoid being stuck in corners
            score = -dist2(nx, ny, ox, oy) + 0.05 * corner_bias + 0.02 * nbr
        else:
            ax = 0 if ox > (w - 1) / 2 else w - 1
            ay = 0 if oy > (h - 1) / 2 else h - 1
            far_corner = dist2(nx, ny, ax, ay)
            score = dist2(nx, ny, ox, oy) + 0.08 * far_corner + 0.03 * nbr

        moves.append((score, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], -t[1], -t[2]), reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]