def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Choose moves that maximize our advantage to the best contested resource.
    # Advantage(res) = dist(op,res) - dist(self,next,res)
    # Break ties by preferring smaller self distance after move, then lexicographic delta via fixed candidate order.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        best_res_adv = -10**18
        best_res_self_dist = 10**18
        for rx, ry in resources:
            adv = king_dist(ox, oy, rx, ry) - king_dist(nx, ny, rx, ry)
            sd = king_dist(nx, ny, rx, ry)
            if adv > best_res_adv or (adv == best_res_adv and sd < best_res_self_dist):
                best_res_adv = adv
                best_res_self_dist = sd
        # Small penalty to avoid wandering when advantage is equal
        score = best_res_adv * 1000 - best_res_self_dist
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]