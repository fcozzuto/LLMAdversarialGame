def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # If a resource exists, move towards the closest one while avoiding stepping onto obstacle or leaving grid.
    if resources:
        # find closest resource by Chebyshev distance
        target = min(resources, key=lambda r: dist(self_pos, r))
        best = (0, 0)
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), target)
            # prefer smaller distance to target
            if best_d is None or d < best_d:
                best = (dx, dy)
                best_d = d
        # avoid moving into opponent's position or adjacent to opponent unnecessarily
        nx, ny = sx + best[0], sy + best[1]
        if (nx, ny) == (ox, oy) or max(abs(nx - ox), abs(ny - oy)) <= 1:
            # try to sidestep away if possible
            for dx, dy in moves:
                tx, ty = sx + dx, sy + dy
                if not in_bounds(tx, ty):
                    continue
                if (tx, ty) in obstacles:
                    continue
                if max(abs(tx - ox), abs(ty - oy)) > 1:
                    return [dx, dy]
            # otherwise stay
            return [0, 0]
        return [best[0], best[1]]

    # No resources left: simple deterministic logic to stay safe and approach center slightly.
    center = (w // 2, h // 2)
    dx = center[0] - sx
    dy = center[1] - sy
    move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    move_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    # prefer moving towards center but avoid obstacles and not stepping onto opponent
    cand = [(move_x, move_y), (0, 0), (move_x, 0), (0, move_y)]
    for dxm, dym in cand:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        return [dxm, dym]

    # If all else fails, stay
    return [0, 0]