def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set((p[0], p[1]) for p in observation.get('obstacles', []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    bs_self = 10**9
    # Prefer resources where we're at least as close as the opponent; otherwise, favor smallest disadvantage.
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # diff positive if we are closer or tied
        diff = opp_d - self_d
        # also lightly prefer nearer resources to finish earlier
        score = (diff, -self_d, -rx, -ry)
        if best is None or score > best:
            best = score
            bs_self = self_d
            target = (rx, ry)

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0, 10**9, 10**9)  # dx,dy,dist,prefer
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # prefer moves that strictly reduce distance; otherwise smallest distance; then deterministic tie-break
        reduce = 1 if nd < cur_d else 0
        prefer = 0 if reduce else 1
        key = (prefer, nd, dx, dy)
        if key < (best_move[2], best_move[3], best_move[0], best_move[1]):
            best_move = (dx, dy, nd, prefer)

    dx, dy = best_move[0], best_move[1]

    # If we couldn't find a valid move (all blocked), stay.
    if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]