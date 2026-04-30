def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Choose resource: prefer where we are closer than opponent; then closer overall; then deterministic coords
    best = None
    for rx, ry in resources:
        md = dist(x, y, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (md - od, md, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        # No visible resources; drift away from opponent while avoiding obstacles
        target = (0 if x < w // 2 else w - 1, 0 if y < h // 2 else h - 1)
    else:
        target = best[1]

    tx, ty = target
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    valid = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    def opp_penalty(nx, ny):
        # discourage stepping onto/next to opponent (if allowed); still deterministic
        d = abs(nx - ox) + abs(ny - oy)
        if d == 0:
            return 10.0
        if d == 1:
            return 2.0
        return 0.0

    # Pick move minimizing distance to target with small opponent avoidance
    best_move = None
    best_score = None
    for dx, dy in valid:
        nx, ny = x + dx, y + dy
        score = dist(nx, ny, tx, ty) + 0.3 * opp_penalty(nx, ny)
        # deterministic tie-break: lexicographic on (score, dx, dy)
        key = (score, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]