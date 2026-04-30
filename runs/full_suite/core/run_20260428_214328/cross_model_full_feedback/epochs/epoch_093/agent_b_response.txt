def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Priority: move toward nearest resource not blocked by obstacle
        closest_r = None
        closest_d = None
        for rx, ry in resources:
            d = dist_cheb((nx, ny), (rx, ry))
            if closest_d is None or d < closest_d:
                closest_d = d
                closest_r = (rx, ry)

        score = 0
        if closest_r is not None:
            score -= closest_d  # closer to resource is better
        # Also prefer staying away from opponent to avoid direct collision, but deterministic
        od = dist_cheb((nx, ny), (ox, oy))
        score -= max(0, 3 - od)  # discourage close approach but allow if needed

        # Avoid immediate trap: penalize landing on opponent's current position
        if (nx, ny) == (ox, oy):
            score -= 1000

        # Favor keeping distance from obstacles adjacency
        adj_obstacles = 0
        for ex, ey in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1),
                       (nx - 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny - 1), (nx + 1, ny + 1)):
            if (ex, ey) in obstacles:
                adj_obstacles += 1
        score -= adj_obstacles

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: if no move improved, stay
    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]