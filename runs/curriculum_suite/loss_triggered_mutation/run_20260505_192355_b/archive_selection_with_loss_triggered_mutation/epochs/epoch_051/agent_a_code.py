def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def cell_adv_for(next_pos):
        if not res:
            # Fallback: move to increase distance from opponent (edge_patrol style) while staying safe
            return -cheb(next_pos, (ox, oy))
        best = None
        # Favor resources where we can arrive not later than opponent; break ties by closeness.
        for r in res:
            sd = cheb(next_pos, r)
            od = cheb((ox, oy), r)
            # Big reward if we are closer or equal; also prefer shorter sd for speed.
            adv = (od - sd) * 10 - sd
            if best is None or adv > best:
                best = adv
        return best if best is not None else -10**9

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Penalize stepping closer to opponent only slightly unless it helps to capture a resource.
        val = cell_adv_for((nx, ny)) - 0.5 * cheb((nx, ny), (ox, oy))
        # Tie-break deterministically by preferring staying if equal advantage, else lexicographic move order.
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]