def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # If no visible resources, drift toward center while avoiding obstacles
    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = (cheb(nx, ny, cx, cy), -nx, -ny)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick the resource opponent is most likely to race for (closest to opponent).
    # If multiple, prefer one where it also benefits their distance relative to us.
    best_target = None
    best_tv = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        tv = (od, - (od - sd), rx, ry)
        if best_tv is None or tv < best_tv:
            best_tv = tv
            best_target = (rx, ry)

    rx, ry = best_target

    # Move to deny: maximize the margin improvement for us vs opponent on that target,
    # with obstacle-aware tie-break toward the target and away from getting too close to opponent.
    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # We want self_d small; also improve our relative standing vs opponent.
        # If opponent is already extremely close, prioritize not stepping into a worse zone by
        # also considering how close we get to opponent directly.
        self_to_opp = cheb(nx, ny, ox, oy)
        score = (self_d - opp_d, self_d, self_to_opp, abs(nx - rx) + abs(ny - ry), -nx, -ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move