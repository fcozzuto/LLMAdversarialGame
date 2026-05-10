def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def sgn(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("guard" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if sx == ox and sy == oy:
        return [0, 0]

    best_dxdy = (0, 0)
    best_val = -10**18 if pursuer else 10**18

    target_dx = sgn(ox - sx)
    target_dy = sgn(oy - sy)

    # deterministic corner bias for evader
    cx, cy = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if not pursuer and nx == ox and ny == oy:
            continue  # avoid immediate capture if applicable

        dxx = nx - ox
        dyy = ny - oy
        dist2 = dxx * dxx + dyy * dyy

        corner_dx = sgn(cx - nx)
        corner_dy = sgn(cy - ny)
        corner_align = 1 if (dx == corner_dx and dy == corner_dy) else 0

        align = 1 if (dx == target_dx and dy == target_dy) else 0
        # obstacles are already handled; add slight preference for tighter approach/escape with alignment
        val = (-dist2) + (3 if align else 0) + (corner_align if not pursuer else 0)
        if not pursuer:
            val = (dist2) + (2 if align else 0) + (2 if corner_align else 0)
        if pursuer:
            if val > best_val:
                best_val = val
                best_dxdy = (dx, dy)
        else:
            if val < best_val:
                best_val = val
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]