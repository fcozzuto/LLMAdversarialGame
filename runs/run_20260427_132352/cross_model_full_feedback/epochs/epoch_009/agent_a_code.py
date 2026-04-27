def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if resources:
        tx, ty = min((tuple(r) for r in resources), key=lambda p: dist(sx, sy, p[0], p[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_to_t = dist(nx, ny, tx, ty)
        d_to_o = dist(nx, ny, ox, oy)

        # Prefer moving toward target; strongly avoid moving into/near opponent.
        # Also lightly prefer staying away from "too close" squares to reduce collisions.
        score = (-2 * d_to_t) + (3 * d_to_o)

        # If opponent is closer to the target than we are, prioritize blocking by increasing distance to opponent.
        my_d = dist(sx, sy, tx, ty)
        op_d = dist(ox, oy, tx, ty)
        if op_d < my_d:
            score += (2 * d_to_o - 4 * dist(nx, ny, ox, oy))

        # Deterministic tie-breaker based on coordinates and turn index.
        ti = int(observation.get("turn_index", 0) or 0)
        tie = ((nx + 1) * 131 + (ny + 1) * 197 + (dx + 2) * 17 + (dy + 2) * 29 + ti) % 1000

        key = (score, -d_to_t, d_to_o, -tie)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move