def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    # Pick a resource where we have (or can gain) tempo over opponent; otherwise take the closest.
    best = None
    best_key = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # Prefer guaranteed-ish claims, then maximize lead, then prioritise nearer
        # (tie-break deterministically by coordinates).
        if lead >= 0:
            key = (0, -lead, ds, rx, ry)  # smaller ds, larger lead via -lead
        else:
            # If we can't beat them, still go for a target that is both relatively close and
            # reduces how far behind we are; also favor reachable soon.
            soon = 0 if (tr <= 0 or ds <= tr) else 1
            key = (1, soon, ds, -lead, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move one step towards target, but don't step into obstacles if avoidable.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            dist = cheb(nx, ny, tx, ty)
            candidates.append((dist, abs(tx - nx) + abs(ty - ny), nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]