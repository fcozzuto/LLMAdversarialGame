def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    def dist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal steps
    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh
    def corners():
        return [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
    # Pick target: resource where we are (relatively) earlier than opponent
    best = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        key = (do - ds, -ds, -r[0], -r[1])  # prefer positive gap, then nearer, then deterministic
        if best_key is None or key > best_key:
            best_key = key
            best = r
    if best is None:
        # No resources: move to corner farthest from opponent
        target = max(corners(), key=lambda c: dist((ox, oy), c) - 0.1 * dist((sx, sy), c))
    else:
        target = best
    # Choose move that reduces distance to target; if tie, maximize separation from opponent
    best_move = [0, 0]
    best_pair = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to = dist((nx, ny), target)
            d_opp = dist((nx, ny), (ox, oy))
            pair = (-d_to, d_opp, dx, dy)  # max -d_to == min d_to; then max d_opp
            if best_pair is None or pair > best_pair:
                best_pair = pair
                best_move = [dx, dy]
    return best_move