def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, move toward the corner that maximizes distance from opponent (escape).
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: man(p[0], p[1], ox, oy))
        best = (0, 0)
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource that we can reach sooner (or least losing).
    best_rx = best_ry = None
    best_score = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets we can claim; lightly prefer closer ones; penalize being behind.
        score = (do - ds) * 10 - ds
        if ds == 0:
            score += 10000
        # If we are behind, still pick if it is our best available contest.
        if score > best_score:
            best_score = score
            best_rx, best_ry = rx, ry

    # Move one step toward the chosen target, preferring moves that are collision-free.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, best_rx, best_ry)
        # Also avoid stepping into immediate opponent advantage when contesting.
        nod = man(ox, oy, best_rx, best_ry)
        val = best_score - (ns * 2) + (nod - ns)  # maximize progress while keeping contest margin
        # Small tie-break: prefer diagonal/forward (toward target) and not staying.
        if (dx, dy) != (0, 0):
            val += 0.1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]