def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def sign(v):
        if v > 0:
            return 1
        if v < 0:
            return -1
        return 0

    # Pick target resource to be first on it (account for opponent)
    if not resources:
        # No visible resources: drift toward center
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        best = None
        tx = ty = None
        for rx, ry in resources:
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            score = (d1 - d2, d1, rx, ry)
            if best is None or score < best:
                best = score
                tx, ty = rx, ry

    if (sx, sy) == (tx, ty):
        return [0, 0]

    desired_dx = sign(tx - sx)
    desired_dy = sign(ty - sy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # If desired step is valid, take it; else choose best move toward target
    if (desired_dx, desired_dy) in {(dx, dy) for dx, dy in moves}:
        return [desired_dx, desired_dy]

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Primary: reduce distance to target, Secondary: prefer intercept advantage
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        score = (d_self - d_opp, d_self, dx, dy)
        if bestm is None or score < bestm:
            bestm = score
            bx, by = dx, dy

    return [int(bx), int(by)]