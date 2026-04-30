def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy)

    def min_dist_to_resources(pos):
        if not resources:
            return 10**9
        return min(dist(pos, r) for r in resources)

    opp_pos = (ox, oy)
    opp_min_d = min_dist_to_resources(opp_pos)

    best = None
    best_val = -10**18
    for dx, dy in moves:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        me_pos = (nx, ny)
        val = 0
        if (nx, ny) in resources:
            val += 1000
        my_min_d = min_dist_to_resources(me_pos)
        val += 10 * (opp_min_d - my_min_d)
        val += 5 * dist(me_pos, opp_pos)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]