def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit")) or ("evader" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def blockiness(x, y):
        c = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + ddx, y + ddy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                c += 1
        return c

    # Deterministic corner preference for evader: run toward the farthest corner from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1]))

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if pursuer:
            # Prefer decreasing manhattan, but also keep away from being "pinched" by obstacles.
            man = abs(nx - ox) + abs(ny - oy)
            val = (0, man, blockiness(nx, ny), dx, dy)
            score = val
            if best_val is None or score < best_val:
                best_val = score
                best = [dx, dy]
        else:
            # Prefer increasing distance; also prefer moving toward chosen farthest corner.
            d = dist2(nx, ny)
            to_corner = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            val = (0, -d, to_corner, blockiness(nx, ny), dx, dy)
            score = val
            if best_val is None or score < best_val:
                best_val = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]