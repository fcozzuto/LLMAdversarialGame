def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ox_set = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Choose deterministic nearest resource
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    target = None
    best = None
    for r in resources:
        d = dist((sx, sy), r)
        tieb = (r[0], r[1])
        if best is None or d < best[0] or (d == best[0] and tieb < best[1]):
            best = (d, tieb)
            target = r

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # Greedy: reduce distance to target, prefer moving away from opponent if equal
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ox_set:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_o = dist((nx, ny), (ox, oy))
        # tie-breakers deterministic
        key = (d_to_t, -d_to_o, abs(dx), abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]