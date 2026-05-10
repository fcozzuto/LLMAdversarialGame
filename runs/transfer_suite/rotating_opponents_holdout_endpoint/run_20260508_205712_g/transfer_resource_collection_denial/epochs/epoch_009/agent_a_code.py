def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", []) if 0 <= r[0] < w and 0 <= r[1] < h]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    # Choose a target that we can reach before the opponent (maximizes advantage).
    best_t = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        sd = man(my, r)
        od = man(opp, r)
        # Prefer resources we can potentially beat; slight tie-break toward closer resources.
        key = (od - sd, -sd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_t = r
    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    # Move one step toward target with a deterministic evaluation of legal moves.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man((nx, ny), (tx, ty))
        # If stepping onto a resource, heavily prioritize it.
        on_res = (tx == nx and ty == ny)
        # Also, add a small "blocking" effect: if we are adjacent to opponent, prefer staying near.
        adj_opp = 1 if man((nx, ny), opp) == 1 else 0
        score = (1 if on_res else 0, adj_opp, -nd, -abs(nx - tx), -abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]