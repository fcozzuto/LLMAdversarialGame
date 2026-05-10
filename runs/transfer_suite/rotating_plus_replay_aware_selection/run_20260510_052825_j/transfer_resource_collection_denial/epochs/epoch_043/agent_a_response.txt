def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        x, y = p[0], p[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later; then maximize "lead",
        # and break ties deterministically.
        reach_adv = od - sd
        key = (0 if sd <= od else 1, -reach_adv, sd, rx * 9 + ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, tx, ty)  # same target, placeholder to keep expression simple
        # Also slightly bias to keep opponent farther from our chosen target.
        opdist = cheb(ox, oy, tx, ty)
        key = (nsd, -opdist, (nx * 9 + ny), 0 if dx == 0 and dy == 0 else 1)
        if bestm is None or key < bestm[0]:
            bestm = (key, (dx, dy))
    if bestm is None:
        return [0, 0]
    dx, dy = bestm[1]
    return [int(dx), int(dy)]