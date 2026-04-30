def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - du  # positive if we arrive earlier
        if best is None:
            best = (adv, -do, -du, rx, ry)
        else:
            cand = (adv, -do, -du, rx, ry)
            if cand > best:
                best = cand
    _, _, _, tx, ty = best

    opp_d_now = cheb(sx, sy, ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    chosen = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        du = cheb(sx, sy, tx, ty)
        du2 = d_t
        # Prefer improving our target progress; if no advantage, fall back to nearest-target.
        adv_move = (du - du2) + (d_o - opp_d_now) * 0.05
        # Tie-break deterministically with lexicographic preference.
        key = (adv_move, -d_t, d_o, -dx, -dy, nx, ny)
        if chosen is None or key > chosen[0]:
            chosen = (key, dx, dy)

    if chosen is None:
        return [0, 0]
    return [int(chosen[1]), int(chosen[2])]