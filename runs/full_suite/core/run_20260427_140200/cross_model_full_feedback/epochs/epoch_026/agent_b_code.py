def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # If a resource is present, move towards the closest resource while considering opponent.
    if resources:
        best_move = None
        best_score = None
        for dx, dy, nx, ny in cand:
            # compute distance to nearest resource from new position
            myd = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            # distance to opponent from new position
            opd = abs(ox - nx) + abs(oy - ny)
            # simple heuristic: favor reducing distance to resource while keeping away from opponent if too close
            score = -myd - max(0, opd - 2)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy, nx, ny)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # fallback: move to reduce distance to a resource if any, else move away from opponent or toward center
    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in cand:
            myd = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            opd = abs(ox - nx) + abs(oy - ny)
            score = -myd + (opd if opd > 0 else 0)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or heuristic fails, simple defensive: move away from opponent if possible
    best_move = None
    best_gap = -1
    for dx, dy, nx, ny in cand:
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        if best_move is None or dist_to_opp > best_gap:
            best_gap = dist_to_opp
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]