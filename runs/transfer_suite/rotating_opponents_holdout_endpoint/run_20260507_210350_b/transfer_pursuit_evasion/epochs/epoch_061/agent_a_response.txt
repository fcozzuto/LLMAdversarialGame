def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def corner_score(x, y):
        if self_is_evader:
            return max(abs(cx - x) + abs(cy - y) for cx, cy in corners)
        else:
            return min(abs(cx - x) + abs(cy - y) for cx, cy in corners)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d2 = dist2(nx, ny, ox, oy)
        cs = corner_score(nx, ny)

        # Heuristic: if evader, maximize distance primarily, then corner; if pursuer, minimize distance primarily, then corner.
        val = (d2, cs) if self_is_evader else (-d2, -cs)
        if best is None or val > best_val:
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]