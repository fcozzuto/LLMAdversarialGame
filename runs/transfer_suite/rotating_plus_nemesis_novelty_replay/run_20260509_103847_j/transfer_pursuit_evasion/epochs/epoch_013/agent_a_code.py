def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_trap_value(x, y):
        best = -10**9
        for cx, cy in corners:
            # prefer being closer to the nearest corner (pinning behavior)
            best = max(best, -(abs(cx - x) + abs(cy - y)))
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Main objective: minimize distance to opponent
        d_opp = dist2(nx, ny, ox, oy)

        # Secondary objective: reduce opponent's freedom by moving toward corners
        # (also adds stability against zig-zag evasion)
        trap = corner_trap_value(nx, ny)

        # Tertiary objective: avoid stepping into "obstacle-adjacent dead zones"
        # Compute how many legal neighboring cells are available from the candidate.
        free_neighbors = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty):
                free_neighbors += 1

        # Higher score is better
        score = (-d_opp) + 0.08 * trap + 0.02 * free_neighbors
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]