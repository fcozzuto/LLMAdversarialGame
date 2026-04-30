def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources, head toward center while avoiding obstacles.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)
    else:
        # Choose resource with best relative advantage (opponent farther than us).
        target = None
        best = None
        for r in resources:
            selfd = dist((sx, sy), r)
            oppd = dist((ox, oy), r)
            # Maximize advantage; tie-break with smaller self distance, then deterministic by position.
            adv = oppd - selfd
            key = (adv, -selfd, -r[0], -r[1])
            if best is None or key > best:
                best = key
                target = r

    tx, ty = target
    # If opponent is adjacent/near, prioritize moving away.
    close = dist((sx, sy), (ox, oy)) <= 1

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Candidate scoring
            if close:
                # Move to maximize distance from opponent.
                score = -dist((nx, ny), (ox, oy))
            else:
                # Move toward target with mild tie-breaking to reduce oscillation near opponent.
                selfd = dist((nx, ny), (tx, ty))
                oppd = dist((nx, ny), (ox, oy))
                score = selfd - 0.15 * oppd
            candidates.append((score, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [candidates[0][3], candidates[0][4]]