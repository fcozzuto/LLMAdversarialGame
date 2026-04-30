def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    best = None
    bestv = -10**18
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        cent = cheb(rx, ry, cx, cy)
        # Prefer stealing: large opponent distance, modest self distance, also avoid center traps lightly.
        v = (d2 * 6) - (d1 * 10) - (cent * 2)
        # Slightly prefer resources not "behind" obstacles: penalize if adjacent to obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (rx + ax, ry + ay) in obstacles:
                    adj += 1
        v -= adj * 3
        if v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # Encourage reducing target distance; also avoid stepping into immediate opponent proximity.
        opp_d = cheb(nx, ny, ox, oy)
        # If tied, prefer staying closer to target and away from opponent; then deterministic order already.
        score = d_to_target * 1000 - opp_d * 7
        moves.append((score, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort()
    return [moves[0][1], moves[0][2]]