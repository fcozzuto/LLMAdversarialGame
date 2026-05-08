def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    sr = (observation.get("self_role", "") or "").lower()
    flee = ("evader" in sr) or ("runner" in sr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if flee:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = None
        best_d = None
        for cx, cy in corners:
            if not free(cx, cy):
                continue
            d = abs(cx - ox) + abs(cy - oy)
            if best_corner is None or d > best_d:
                best_corner, best_d = (cx, cy), d
        if best_corner is None:
            best_corner = corners[0]

        tcx, tcy = best_corner
        best_move, best_val = (0, 0), None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist_to_corner = abs(tcx - nx) + abs(tcy - ny)
            dist_from_p = abs(ox - nx) + abs(oy - ny)
            val = (dist_from_p * 10) - dist_to_corner
            if best_val is None or val > best_val:
                best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move, best_val = (0, 0), None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = max(abs(nx - ox), abs(ny - oy))  # diagonal-friendly
        # tie-break: move that also keeps obstacle pressure (prefer advancing along axes if md tied)
        ad = abs(nx - ox) + abs(ny - oy)
        adv = (ad)
        val = (-md * 100) - adv
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]