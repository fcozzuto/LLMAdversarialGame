def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            ds = dist((x, y), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            score = (do - ds, -ds, -(abs(rx - (w - 1 - x)) + abs(ry - (h - 1 - y))), rx, ry)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        # No visible resources: move toward center-ish to reduce chance of being blocked
        tx, ty = (w // 2, h // 2)

    dx = 0
    dy = 0
    if tx > x: dx = 1
    elif tx < x: dx = -1
    if ty > y: dy = 1
    elif ty < y: dy = -1

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    # Add any remaining neighbors deterministically
    for nx in (-1, 0, 1):
        for ny in (-1, 0, 1):
            if (nx, ny) not in candidates:
                candidates.append((nx, ny))

    def valid(nx, ny):
        nxp, nyp = x + nx, y + ny
        return 0 <= nxp < w and 0 <= nyp < h and (nxp, nyp) not in obstacles

    best_move = (0, 0)
    best_val = None
    for mx, my in candidates:
        if not valid(mx, my):
            continue
        nxp, nyp = x + mx, y + my
        # Prefer closer to target; if equal, prefer farther from opponent
        v = (-(dist((nxp, nyp), (tx, ty))), dist((nxp, nyp), (ox, oy)), mx, my)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]