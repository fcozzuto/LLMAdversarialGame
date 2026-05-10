def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def md(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - ds  # positive means we arrive first
        penalty = 0
        if ry == oy and do <= ds:
            penalty += 2
        if rx == ox and do <= ds:
            penalty += 1
        key = (adv - penalty, -ds, do)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    options = []
    for m_dx in (dx, 0, -dx):
        for m_dy in (dy, 0, -dy):
            if m_dx == 0 and m_dy == 0:
                options.append((0, 0))
            else:
                options.append((m_dx, m_dy))
    seen = set()
    ordered = []
    for m in options:
        if m not in seen:
            seen.add(m)
            ordered.append(m)

    best_move = (0, 0)
    best_dist = None
    for m_dx, m_dy in ordered:
        nx, ny = sx + m_dx, sy + m_dy
        if not legal(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (m_dx, m_dy) == (dx, dy)):
            best_dist = d
            best_move = (m_dx, m_dy)

    return [best_move[0], best_move[1]]