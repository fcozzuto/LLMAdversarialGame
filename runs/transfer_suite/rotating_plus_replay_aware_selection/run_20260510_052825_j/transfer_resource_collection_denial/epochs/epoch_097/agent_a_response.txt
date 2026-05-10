def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_list}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = None

    # Choose a "contested" target deterministically.
    # Give priority to resources we can reach no slower than opponent; otherwise, reduce distance to best swing target.
    candidates = []
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        immediate = 1000 if sd <= 0 else 0
        swing = (od - sd)  # positive means we are closer or equal
        # Prefer nearer targets when swing is similar; mild bias toward lower y then x for determinism.
        tie = (-sd * 2) + (-rx * 0.001) + (-ry * 0.0001)
        candidates.append((-(swing * 10 + tie) - immediate, sd, od, rx, ry))
    if not candidates:
        return [0, 0]
    candidates.sort()
    top = candidates[:3]  # small deterministic set

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy

        # Score move by resulting advantage against top targets; include small penalty if we don't improve.
        move_score = 0
        for _, sd, od, rx, ry in top:
            nsd = cheb(nx, ny, rx, ry)
            nod = cheb(ox, oy, rx, ry)
            if nsd == 0:
                move_score += 5000  # immediate collection
            # Prefer making ourselves at least as fast as opponent for the same target.
            move_score += (nod - nsd) * 100 - nsd
            # Encourage improvement vs current distance for that target.
            move_score += (sd - nsd) * 20

        # Tiny deterministic tie-break toward staying central-ish.
        move_score += -abs(nx - (w - 1) / 2) * 0.01 - abs(ny - (h - 1) / 2) * 0.01

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_dx, best_dy = nx - sx, ny - sy

    return [int(best_dx), int(best_dy)]