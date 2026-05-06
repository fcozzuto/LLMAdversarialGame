def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def edge_penalty(x, y):
        return 2 if x in (0, w - 1) or y in (0, h - 1) else 0

    if not resources:
        best = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dopp = dist(nx, ny, ox, oy)
            key = (dopp, -edge_penalty(nx, ny), -(abs(nx - (w - 1 - ox)) + abs(ny - (h - 1 - oy))), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = None
    # Two-stage: pick a "contested target" then score moves by progress to it and safety vs opponent
    # Contested target = resource where we are not much farther than opponent (or are closer).
    contested = []
    for rx, ry in resources:
        d_s = dist(sx, sy, rx, ry)
        d_o = dist(ox, oy, rx, ry)
        advantage = d_o - d_s  # positive if we are closer
        if advantage >= -2:  # allow slightly worse to reduce brittleness
            contested.append((advantage, d_s + d_o, rx, ry))
    if not contested:
        contested = [(dist(sx, sy, rx, ry) - dist(ox, oy, rx, ry), dist(sx, sy, rx, ry), rx, ry) for rx, ry in resources]

    contested.sort(reverse=True)
    tx, ty = contested[0][2], contested[0][3]

    # Also keep a simple goal toward center to avoid getting stuck
    center_x, center_y = (w - 1) // 2, (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dtx0 = dist(sx, sy, tx, ty)
        dtx1 = dist(nx, ny, tx, ty)
        progress = dtx0 - dtx1  # positive if closer

        # Safety: prefer moves that reduce opponent access to same target
        d_o0 = dist(ox, oy, tx, ty)
        d_o1 = dist(ox, oy, tx, ty)  # opponent not moving; keep static compare for determinism
        # Actual safety term uses relative closeness after our move:
        opp_closer_after = dist(nx, ny, tx, ty) - dist(ox, oy, tx, ty)

        # Resource capture heuristic: if we step onto a resource cell, huge value
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        # Avoid letting opponent get too close
        dopp = dist(nx, ny, ox, oy)
        safety = dopp

        key_val = (10 * on_res + 3 * progress - 2 * opp_closer_after + 0.2 * safety
                   - 0.1 * edge_penalty(nx, ny)
                   - 0.05 * dist(nx, ny, center_x, center_y))

        if best_val is None or key_val > best_val:
            best_val = key_val
            best_move = [dx, dy]

    return best_move