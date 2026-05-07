def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            cand.append((dx, dy, nx, ny))

    def mdist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    # Primary: maximize race lead after move (opp_dist - me_dist). Secondary: minimize my dist, then prefer diagonals.
    for dx, dy, nx, ny in cand:
        my_best = None
        for rx, ry in resources:
            d_me = mdist(nx, ny, rx, ry)
            d_op = mdist(ox, oy, rx, ry)
            lead = d_op - d_me
            # Prefer taking immediate-ish resources with positive lead; otherwise contest nearest.
            key = (lead, -d_me, -(abs(dx) + abs(dy) == 2), -(abs(nx - rx) + abs(ny - ry) == 0))
            if my_best is None or key > my_best:
                my_best = key
        if my_best is None:
            continue
        # Break ties deterministically by choosing lexicographically smallest move delta among equals.
        move_key = (my_best[0], my_best[1], my_best[2], my_best[3], -abs(dx), -abs(dy), dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]