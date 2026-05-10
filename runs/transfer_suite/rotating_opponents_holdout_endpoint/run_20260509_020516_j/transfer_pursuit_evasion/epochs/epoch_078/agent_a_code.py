def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) and ("evader" not in opp_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev distance
        if is_evader:
            # maximize distance; prefer hugging edges (wall-run style) while switching edge bias away from opponent
            score = (dist * 1000) + (-(edge_dist(nx, ny)) * 10)
            # discourage moving toward the opponent's closest edge
            opp_min_edge = edge_dist(ox, oy)
            my_min_edge = edge_dist(nx, ny)
            score += (my_min_edge - opp_min_edge) * 2
        else:
            # pursuer: minimize distance; avoid obstacles; lightly prefer pushing opponent toward edges
            score = (-dist * 1000) + (edge_dist(nx, ny) * -1)
            # encourage approach that reduces opponent's edge distance (push to wall)
            score += (-(edge_dist(ox, oy)) * 0.5)
        key = (score, dx, dy)
        if best is None or key > best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]
    _, dx, dy = best
    return [int(dx), int(dy)]