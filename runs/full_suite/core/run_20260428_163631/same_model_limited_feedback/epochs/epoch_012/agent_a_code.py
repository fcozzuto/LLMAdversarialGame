def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        dx = 0
        dy = 0
        # drift toward center
        tx, ty = (W - 1) / 2.0, (H - 1) / 2.0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach significantly earlier; then closest
        key = (dO - dS, -dS, -(cheb(ox, oy, sx, sy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    candidates = []
    deltas = (-1, 0, 1)
    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            dT = cheb(nx, ny, tx, ty)
            dO_next = cheb(nx, ny, ox, oy)
            # Prefer reducing distance to target; also prefer staying away from opponent
            score = (-dT, dO_next, -(dx != 0 and dy != 0), -abs(dx) - abs(dy))
            candidates.append((score, dx, dy))
    candidates.sort(reverse=True)
    if candidates:
        return [int(candidates[0][1]), int(candidates[0][2])]
    return [0, 0]