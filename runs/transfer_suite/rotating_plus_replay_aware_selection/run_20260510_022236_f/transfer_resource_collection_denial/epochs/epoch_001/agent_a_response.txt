def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sp = observation.get('self_position', [0, 0])
    op = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)
    sx, sy = sp
    ox, oy = op

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx <= -0 else -dx  # avoid extra ops
    # simpler deterministic cheb without tricks
    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ad = cheb_dist(sx, sy, rx, ry)
        bd = cheb_dist(ox, oy, rx, ry)
        # Prefer resources we can reach no later; then lower our distance; then earlier "turns" bias
        can = 1 if ad <= bd else 0
        key = (0 if can == 1 else 1, ad - bd, ad, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    curd = cheb_dist(sx, sy, tx, ty)
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        nd = cheb_dist(nx, ny, tx, ty)
        # Move that most reduces distance; tie-break by smallest resulting dist and lexicographic move
        mkey = (nd, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    if cheb_dist(sx + best_move[0], sy + best_move[1], tx, ty) > curd:
        return [0, 0]
    return best_move