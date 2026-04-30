def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        x, y = p
        x = int(x); y = int(y)
        if inb(x, y): obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = r
        x = int(x); y = int(y)
        if inb(x, y) and (x, y) not in obst:
            resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if resources:
        opp_target = min(resources, key=lambda p: (cheb((ox, oy), p), p[0], p[1]))
        all_target_list = resources
    else:
        opp_target = (ox, oy)
        all_target_list = [(sx, sy), (ox, oy)]

    opp_d = cheb((ox, oy), opp_target)

    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_opp_comp = cheb((nx, ny), opp_target) - opp_d  # smaller is better (intercept/deny)
        my_near_any = min(cheb((nx, ny), r) for r in all_target_list) if all_target_list else 0
        # Prefer closer-to-any resources, and also deny opponent's closest target.
        val = (my_opp_comp, my_near_any, nx, ny)
        if best is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]