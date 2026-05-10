def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # One-ply lookahead: pick move that maximizes immediate pickup + future advantage over opponent.
    best = None
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place
        # If we are already on a resource, it must be collected this turn; prioritize that.
        pickup = 1_000_000 if (nx, ny) in res_set else 0
        # Choose the best resource "seen" from next position.
        best_adv = -10**9
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Higher is better: we want od - sd, plus a small preference for shorter sd.
            val = (od - sd) * 1000 - sd
            if val > best_adv:
                best_adv = val
        # Tie-break deterministically by favoring shorter immediate travel, then lexicographic dx,dy.
        key = (-(pickup + best_adv), cheb(sx, sy, nx, ny), dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]