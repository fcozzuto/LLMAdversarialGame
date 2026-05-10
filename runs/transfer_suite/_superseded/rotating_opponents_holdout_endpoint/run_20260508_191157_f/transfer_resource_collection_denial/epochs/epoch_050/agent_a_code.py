def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_u = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            center_b = 0.01 * (abs(rx - cx) + abs(ry - cy))
            u = (od - sd) * 100.0 - 0.7 * sd - center_b
            if best is None or u > best_u or (u == best_u and (rx, ry) < best):
                best_u = u
                best = (rx, ry)
        tx, ty = best

    # Prefer moves that get closer to target while staying ahead of opponent; avoid obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                moves.append(( -10**9, dx, dy, nx, ny))
            else:
                sd2 = man(nx, ny, tx, ty)
                od2 = man(ox, oy, tx, ty)
                # Encourage increasing our lead; slight penalty for obstacles/edge proximity via distance to center.
                edge_pen = 0.001 * ((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)
                lead = od2 - sd2
                u = lead * 50.0 - sd2 - edge_pen
                moves.append((u, dx, dy, nx, ny))

    moves.sort(key=lambda t: (-t[0], t[3], t[4], t[1], t[2]))
    _, dx, dy, _, _ = moves[0]
    return [int(dx), int(dy)]