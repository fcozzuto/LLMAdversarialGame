def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", sp) or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_cells(lst):
        out = []
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
        return out

    obstacles = set(to_cells(observation.get("obstacles", []) or []))
    unclaimed = to_cells(observation.get("unclaimed_cells", []) or [])
    self_terr = set(to_cells(observation.get("self_territory", []) or []))
    opp_terr = set(to_cells(observation.get("opponent_territory", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []

    nearest_unclaimed = None
    if unclaimed:
        nearest_unclaimed = min(unclaimed, key=lambda p: (dist((sx, sy), p), p[0], p[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        np = (nx, ny)

        # Main objective: move toward unclaimed; when landing on unclaimed, big reward
        if nearest_unclaimed is not None:
            d0 = dist((sx, sy), nearest_unclaimed)
            d1 = dist(np, nearest_unclaimed)
            score += (d0 - d1) * 8
            if np in unclaimed:
                score += 120

        # Territorial play: prefer stepping into our own territory (stability) or expanding boundary
        if np in self_terr:
            score += 10
        if np in opp_terr:
            # Flipping allowed: encourage captures but avoid suicide traps near opponent
            score += 70

        # Boundary expansion: prefer moving to cells adjacent to our territory when we are stuck
        if not unclaimed:
            for tx, ty in self_terr:
                pass
            # lightweight adjacency bonus
            adj_self = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in self_terr:
                        adj_self += 1
            score += adj_self * 6

        # Avoid proximity to opponent (deterministic safety)
        d_op = dist(np, (ox, oy))
        score += max(-40, (7 - d_op) * 6)

        # Slight preference for edge/corners to increase territory reach
        edge_bonus = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_bonus = 8
        score += edge_bonus

        # Deterministic tie-break: lexicographic by (score, -d_op, x, y)
        candidates.append((score, -d_op, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, _, best_dx, best_dy = candidates[0]
    return [int(best_dx), int(best_dy)]