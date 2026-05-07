def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        # Prefer resources we can reach sooner (large margin), then closer by self distance, then top-left deterministically.
        key = (margin, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    (rx, ry) = best[1]

    # If opponent is already strictly closer to every resource, still move toward the best one to contest.
    cur_to_target = cheb(sx, sy, rx, ry)

    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_after = cheb(nx, ny, rx, ry)
        # Strongly prefer reducing distance; break ties by staying closer to target and away from opponent.
        opp_after = cheb(nx, ny, ox, oy)
        score = (cur_to_target - d_after, -d_after, -(opp_after - d_after), -nx, -ny)
        scored.append((score, (dx, dy)))
    if not scored:
        return [0, 0]

    scored.sort(reverse=True)
    return [int(scored[0][1][0]), int(scored[0][1][1])]