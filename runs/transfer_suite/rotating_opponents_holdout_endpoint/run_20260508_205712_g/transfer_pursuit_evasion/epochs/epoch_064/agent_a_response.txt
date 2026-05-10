def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "pursuer")).lower()
    pursuer = role != "evader"

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners = [c for c in corners if valid(c[0], c[1])]
    if not corners:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best_dx, best_dy = 0, 0
    if pursuer:
        best = 10**9
        # If we can capture immediately, do it.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and nx == ox and ny == oy:
                return [dx, dy]
        # Greedy: minimize Chebyshev distance; break ties toward moving closer in both coords.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < best:
                best = d
                best_dx, best_dy = dx, dy
            elif d == best:
                cur = abs(nx - ox) + abs(ny - oy)
                prev = abs((sx + best_dx) - ox) + abs((sy + best_dy) - oy)
                if cur < prev:
                    best_dx, best_dy = dx, dy
    else:
        # Evader: maximize distance; prefer heading toward a farthest corner when not blocked.
        target_corner = corners[0]
        if corners:
            for c in corners:
                if cheb(sx, sy, c[0], c[1]) > cheb(sx, sy, target_corner[0], target_corner[1]):
                    target_corner = c
        best = -1
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = cheb(nx, ny, ox, oy)
            # tie-break: prefer increasing distance from pursuer and moving toward the chosen corner
            cdist = cheb(nx, ny, target_corner[0], target_corner[1])
            if d1 > best:
                best = d1
                best_dx, best_dy = dx, dy
            elif d1 == best:
                cur_cdist = cdist
                prev_cdist = cheb(sx + best_dx, sy + best_dy, target_corner[0], target_corner[1])
                if cur_cdist > prev_cdist:
                    best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]