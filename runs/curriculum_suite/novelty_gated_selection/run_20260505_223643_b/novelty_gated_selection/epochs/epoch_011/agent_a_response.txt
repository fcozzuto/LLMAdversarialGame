def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick a target that we can reach first, while also being annoying if opponent gets there.
    best_target = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds) * 12.0
        if do - ds >= 0:
            val += 7.0
        val += 0.1 * (ds - cheb(ox, oy, rx, ry)) * -0.5  # small stabilizer
        val += 0.001 * ((rx + 3 * ry + 7) % 11)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    def step_score(nx, ny):
        # If move hits obstacle or leaves grid, it's invalid (stay will happen anyway; penalize).
        if (not inb(nx, ny)) or (nx, ny) in obstacles:
            return -10**9
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer reducing distance; also keep parity-like tie-break to avoid dithering.
        # Additionally, avoid moving away from target too much.
        return (do - ds) * 10.0 + (-ds) * 1.2 + 0.0005 * ((nx * 3 + ny * 5) % 17)

    best_move = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ms = step_score(nx, ny)
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]