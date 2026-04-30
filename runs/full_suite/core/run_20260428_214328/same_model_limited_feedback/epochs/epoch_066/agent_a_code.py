def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        resources = []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)
    # Choose a target resource where we are relatively closer than the opponent
    tx, ty = sx, sy
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        key = (ds - do, ds, ((rx + ry) & 1))
        if best is None or key < best:
            best = key
            tx, ty = rx, ry
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Evaluate moves: minimize distance to target, maximize distance to opponent, avoid obstacles/out-of-bounds
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtn = md(nx, ny, tx, ty)
        don = md(nx, ny, ox, oy)
        # Tie-break deterministically using turn parity and position
        val = (dtn, -don, ((nx + ny + observation.get("turn_index", 0)) & 1))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]