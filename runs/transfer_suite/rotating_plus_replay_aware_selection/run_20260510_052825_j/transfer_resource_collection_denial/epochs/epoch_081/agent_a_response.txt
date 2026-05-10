def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal_pos(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose best resource target for us based on distance advantage vs opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if not legal_pos(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (-(od - sd), sd, od, rx, ry)  # maximize (od-sd), then closer, then tie by coords
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    # Fallback: no reachable resource cells (should be rare).
    if best_res is None:
        return [0, 0]

    tx, ty = best_res

    # Next move: among legal deltas, maximize resulting advantage to this target.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal_pos(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Slightly prefer progress and staying out of obvious dead-ends.
        dist_to_target = nsd
        # Dead-end heuristic: number of legal neighbors (including stay).
        neigh = 0
        for ddx, ddy in dirs:
            px, py = nx + ddx, ny + ddy
            if legal_pos(px, py):
                neigh += 1
        key = (-(nod - dist_to_target), dist_to_target, -neigh, tx, ty, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    # Ensure deterministic valid return
    return [int(best_move[0]), int(best_move[1])]