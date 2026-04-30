def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = cheb(nx, ny, tx, ty)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Sort resources deterministically: prefer those that are "good targets" for us.
    def res_key(r):
        rx, ry = r
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        return (-(dop - dme), dme, rx, ry)  # higher race advantage first
    resources_sorted = sorted(resources, key=res_key)
    candidates = resources_sorted[:8]

    # Choose move that maximizes expected race advantage on best remaining target.
    best = None
    for dx, dy, nx, ny in moves:
        score = -10**9
        for rx, ry in candidates:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer winning the race; also prefer closer resources even if opponent also close.
            race_adv = opp_d - our_d
            tie_break = -(our_d) + 0.02 * (w - 1 - abs(rx - (w - 1) / 2.0)) + 0.02 * (h - 1 - abs(ry - (h - 1) / 2.0))
            v = 10 * race_adv + tie_break
            if v > score:
                score = v
        # Small deterministic anti-stall: prefer moves that reduce our distance to chosen target set
        if score > -10**8:
            if best is None or score > best[0]:
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]