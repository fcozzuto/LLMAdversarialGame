def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def nearest_res(px, py):
        if not resources:
            return (w - 1, h - 1)
        best = None
        for rx, ry in resources:
            d = man(px, py, int(rx), int(ry))
            if best is None or d < best[0]:
                best = (d, int(rx), int(ry))
        return (best[1], best[2])

    tx, ty = nearest_res(sx, sy)
    otx, oty = nearest_res(ox, oy)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        odx, ody = 0, 0
        # simple opponent-advance assumption: reduce distance to its nearest resource
        if man(ox + 1, oy, otx, oty) < man(ox - 1, oy, otx, oty): odx = 1
        elif man(ox + 1, oy, otx, oty) > man(ox - 1, oy, otx, oty): odx = -1
        if man(ox, oy + 1, otx, oty) < man(ox, oy - 1, otx, oty): ody = 1
        elif man(ox, oy + 1, otx, oty) > man(ox, oy - 1, otx, oty): ody = -1
        nox, noy = ox + odx, oy + ody
        if not inb(nox, noy) or (nox, noy) in obst:
            nox, noy = ox, oy

        self_to_my = man(nx, ny, tx, ty)
        opp_to_my_after = man(nox, noy, tx, ty)
        self_to_opp = man(nx, ny, ox, oy)
        opp_to_target = man(nox, noy, otx, oty)

        val = (-2.0 * self_to_my) + (1.2 * opp_to_my_after) + (0.3 * (opp_to_target)) - (0.05 * self_to_opp)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]