def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    is_pursuer = (observation.get("self_role", "pursuer") == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
    # Deterministic move preference to break ties: favor x first, then y, then stay.
    pref = {(dx, dy): (0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1)) for dx, dy in moves}

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist_to_op = d2(nx, ny, ox, oy)
        if is_pursuer:
            # Greedy chase + discourage "cornering yourself" too early: keep room by slightly preferring moves that
            # reduce distance and also move toward the opponent's position in both axes.
            dxs = 0 if nx == ox else (1 if nx > ox else -1)
            dys = 0 if ny == oy else (1 if ny > oy else -1)
            axis_progress = -abs((nx - ox) != 0) - abs((ny - oy) != 0)
            # Lower is better: minimize distance, then maximize axis matching (both signs).
            val = dist_to_op + (0 if dxs == (1 if ox > sx else -1) or nx == ox else 4) + (0 if dys == (1 if oy > sy else -1) or ny == oy else 4) + (0 if axis_progress else 0)
            better = (best_val is None) or (val < best_val) or (val == best_val and pref[(dx, dy)] < pref[tuple(best)])
        else:
            # Evader: maximize distance from pursuer, but bias toward the farthest corner from the pursuer to exploit corner evasion.
            dist_to_op = d2(nx, ny, ox, oy)
            dist_to_corner = d2(nx, ny, far_corner[0], far_corner[1])
            # Higher is better.
            val = dist_to_op * 3 + dist_to_corner
            better = (best_val is None) or (val > best_val) or (val == best_val and pref[(dx, dy)] < pref[tuple(best)] if best is not None else True)

        if better:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]