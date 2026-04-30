def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(a, b, c, d):
        dx = a - c; dy = b - d
        return dx if dx >= 0 else -dx if dy == 0 else max(dx if dx >= 0 else -dx, dy if dy >= 0 else -dy)

    def dist(a, b, c, d):
        ad = a - c; bd = b - d
        if ad < 0: ad = -ad
        if bd < 0: bd = -bd
        return ad if ad > bd else bd

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    best_key = None
    if resources:
        for r in resources:
            rx, ry = r
            ts = dist(sx, sy, rx, ry)
            to = dist(ox, oy, rx, ry)
            # Prefer resources where we are not slower; break ties deterministically
            key = (ts - to, ts, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
    else:
        best_target = (sx, sy)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        ds = dist(nx, ny, tx, ty)
        do = dist(nx, ny, ox, oy)
        # If on target, take it
        score = (-ds, -do, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If every move is blocked (rare), stay
    return [int(best_move[0]), int(best_move[1])]