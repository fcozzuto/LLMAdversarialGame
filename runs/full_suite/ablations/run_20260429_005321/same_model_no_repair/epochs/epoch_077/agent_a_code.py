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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        if (rx, ry) in obst:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # want positive lead (we can arrive no later)
        # Choose target to maximize lead; if tie, prefer shorter self distance; then deterministic parity/index.
        key = (-lead, ds, ((rx + ry) & 1), i, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Move greedily toward target, but if multiple, bias away from opponent to reduce contest.
    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in legal:
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: maximize distance to opponent; Tertiary: deterministic lex.
        key = (d_to_t, -d_to_o, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]