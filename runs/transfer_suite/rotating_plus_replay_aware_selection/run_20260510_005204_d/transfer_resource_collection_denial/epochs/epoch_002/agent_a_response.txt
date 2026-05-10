def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        for x, y in resources:
            d_my = md(sx, sy, x, y)
            d_opp = md(ox, oy, x, y)
            # Prefer resources closer to me and farther from opponent (materially different targeting)
            key = (d_my - d_opp, d_my, x, y)
            if best is None or key < best[0]:
                best = (key, x, y)
        tx, ty = best[1], best[2]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Evaluate next step against target and opponent
            my_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            # Encourage progress, penalize getting closer to opponent (reduce their race advantage)
            # Also slight center bias to break ties deterministically.
            cx, cy = w / 2.0, h / 2.0
            center_pen = abs(nx - cx) + abs(ny - cy)
            score = (my_d - opp_d, my_d, center_pen, dx, dy)
            candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [candidates[0][1], candidates[0][2]]