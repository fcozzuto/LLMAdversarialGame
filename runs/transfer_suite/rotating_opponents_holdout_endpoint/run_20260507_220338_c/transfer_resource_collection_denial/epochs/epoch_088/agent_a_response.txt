def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                moves.append((dx, dy))

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we're closer to than opponent; then prefer smaller own distance; then deterministic tie
            key = (d_me - d_op, d_me, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2), (h // 2)

    def move_key(dx, dy):
        nx, ny = sx + dx, sy + dy
        d_me = cheb(nx, ny, tx, ty)
        # Deny: move that also makes opponent farther from same target
        d_op = cheb(ox, oy, tx, ty)
        d_op_after = cheb(ox + 0, oy + 0, tx, ty)  # deterministic constant, but keep structure
        # Add tiny preference to reduce distance between us and opponent if opponent is very near target
        opp_near = cheb(ox, oy, tx, ty)
        # deterministic tie-break using position
        return (d_me, -opp_near, (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty), nx, ny)

    best_move = None
    best_mkey = None
    for dx, dy in legal:
        k = move_key(dx, dy)
        if best_mkey is None or k < best_mkey:
            best_mkey = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]