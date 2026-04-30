def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Score resources by how much earlier we can arrive than opponent, then prefer closer/low index.
    best = None
    for i, (rx, ry) in enumerate(resources):
        if (rx, ry) in obst:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # bigger is better
        score = (-lead, ds, i)  # lexicographic min
        if best is None or score < best[0]:
            best = (score, (rx, ry), ds, do)
    if best is None:
        return [0, 0]

    tx, ty = best[1]

    # Move greedily toward target; if multiple, prefer improving our lead and reducing our distance.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nds = cheb(nx, ny, tx, ty)
        # Opponent static approximation: prefer our progress relative to opponent distance to target.
        ndo = cheb(ox, oy, tx, ty)
        lead = ndo - nds
        key = (-lead, nds, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    return best_move[1]