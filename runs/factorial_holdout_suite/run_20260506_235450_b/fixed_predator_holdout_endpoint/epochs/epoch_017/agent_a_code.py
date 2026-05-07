def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_list}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    if not resources:
        return [0, 0]

    # Pick target with a different bias: fast win if ahead; otherwise reduce being behind.
    ahead = []
    behind = []
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd < od:
            ahead.append((sd, -(od - sd), rx, ry))
        else:
            behind.append(((sd - od), sd, rx, ry))
    if ahead:
        ahead.sort()
        _, _, tx, ty = ahead[0]
    else:
        behind.sort()
        _, _, tx, ty = behind[0]

    # Choose move that best advances toward target while also denying (increase opponent distance relative).
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        self_to = md(nx, ny, tx, ty)
        opp_to = md(nx, ny, ox, oy)
        # denial term: we want opponent farther from this target and/or ourselves closer to it
        opp_target = md(ox, oy, tx, ty)
        score = (self_to, opp_target - md(nx, ny, tx, ty), -opp_to, dx, dy)
        if best is None or score < best:
            best = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]