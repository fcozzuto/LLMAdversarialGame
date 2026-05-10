def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("evader" not in self_role) or ("purs" in opp_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sgn(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    if not is_pursuer:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = (-(abs(tx - nx) + abs(ty - ny)), -max(abs(nx - ox), abs(ny - oy)))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        align_x = 1 if nx == ox else 0
        align_y = 1 if ny == oy else 0
        # "Cutoff": prefer moving to reduce both coordinate gaps, not just distance.
        gapx = abs(nx - ox)
        gapy = abs(ny - oy)
        toward_x = 0 if dx == 0 else (1 if sgn(ox - sx) == sgn(dx) else -1)
        toward_y = 0 if dy == 0 else (1 if sgn(oy - sy) == sgn(dy) else -1)
        wall_pen = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        v = (-(dist), 2 * (align_x + align_y), -(gapx + gapy), (toward_x + toward_y), -wall_pen)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]