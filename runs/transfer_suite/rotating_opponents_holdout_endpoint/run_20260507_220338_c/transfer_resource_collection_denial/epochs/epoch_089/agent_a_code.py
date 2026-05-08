def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Base: find closest for us; if opponent is not worse, switch to a "contested" safer target.
    scored = []
    min_self = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        scored.append((rx, ry, sd, od))
        if sd < min_self:
            min_self = sd

    contested_exists = False
    for rx, ry, sd, od in scored:
        if od <= sd:
            contested_exists = True
            break

    if contested_exists:
        # Choose among near-enough resources a target that is farthest from the opponent.
        cand = [t for t in scored if t[2] <= min_self + 2]
        cand.sort(key=lambda t: (-t[3], t[2], t[0], t[1]))
        tx, ty = cand[0][0], cand[0][1]
    else:
        # Choose a resource that maximizes advantage, then prefers shorter self distance.
        scored.sort(key=lambda t: (-(t[3] - t[2]), t[2], t[0], t[1]))
        tx, ty = scored[0][0], scored[0][1]

    # Step greedily toward target with deterministic tie-breaking.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        key = (d, abs(dx), abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]