def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = observation["obstacles"]
    occ = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    def md(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx*dx + dy*dy)

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in occ

    # Pick target deterministically: best immediate claim potential.
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r
        d_self = md((x, y), (rx, ry))
        d_opp = md((ox, oy), (rx, ry))
        key = (d_self - d_opp, d_self, -d_opp, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d_self_next = md((nx, ny), (rx, ry))
            d_opp_curr = md((ox, oy), (rx, ry))
            d_self_curr = md((x, y), (rx, ry))
            # Prefer moves that improve distance-to-target and also improve relative claim.
            adv_curr = d_opp_curr - d_self_curr
            adv_next = d_opp_curr - d_self_next
            step_key = (-adv_next, d_self_next, abs(nx - rx) + abs(ny - ry), dx, dy)
            candidates.append((step_key, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]