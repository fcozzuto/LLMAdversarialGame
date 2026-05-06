def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Select a target resource by deterministic advantage with opponent proximity penalty.
    best = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        # If opponent is very close to this resource, we heavily penalize to force switching.
        prox_pen = 0
        if d_opp <= 2:
            prox_pen = 1000
        # Prefer lower (d_me - d_opp), then closer to center of board to reduce stalemates.
        cx, cy = w // 2, h // 2
        center_bias = md(rx, ry, cx, cy)
        key = (d_me - d_opp + prox_pen, d_me + 2 * center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, move toward center while avoiding obstacles.
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Local step: choose move that reduces our distance to target while also avoiding giving opponent immediate reach.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Our progress
        my = md(nx, ny, tx, ty)
        # Opponent "threat": how much closer opponent would be next if we move into a position that helps them.
        opp = md(ox, oy, tx, ty) - md(ox, oy, nx, ny)
        # Extra: discourage stepping adjacent to obstacles traps by preferring moves with more valid neighbors.
        nbrs = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if valid(ax, ay):
                nbrs += 1
        # Deterministic tie-break: lexicographic.
        val = (my, -(nbrs), -opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]