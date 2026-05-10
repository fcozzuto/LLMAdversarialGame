def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny):
                cnt += 1
        return cnt

    # Strategy: chase greedily, but prefer moves that reduce opponent escape routes (low mobility).
    best_dx, best_dy = 0, 0
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist(nx, ny)
        m = mobility(nx, ny)
        # Key: smallest distance; then smallest mobility (more constrained); then deterministic tie-break.
        key = (d, m, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]