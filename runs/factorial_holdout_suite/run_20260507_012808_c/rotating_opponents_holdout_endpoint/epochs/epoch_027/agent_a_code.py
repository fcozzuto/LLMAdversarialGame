def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev, diagonal cost 1

    def cell_key(x, y):
        # Prefer cells that reduce our distance to resources while keeping away from opponent.
        if resources:
            best = None
            for rx, ry in resources:
                sd = dist(x, y, rx, ry)
                od = dist(ox, oy, rx, ry)
                # If opponent is likely to grab it first (od < sd), penalize heavily.
                score = (od - sd) * 10 - sd
                if best is None or score > best:
                    best = score
            # Small center bias to break ties deterministically
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score2 = best - 0.01 * dist(x, y, int(cx), int(cy))
            return score2
        # No resources: drift toward center while maximizing distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return 0.02 * dist(x, y, int(cx), int(cy)) - 0.05 * dist(x, y, ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = cell_key(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]