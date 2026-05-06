def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        resources = [(cx, cy)]

    best = None
    opp_s = ox + oy
    opp_d = ox - oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # resource priority
        rd = 10**9
        for rx, ry in resources:
            dd = abs(nx - rx) + abs(ny - ry)
            if dd < rd:
                rd = dd
        # break diagonal probing: stay away from opponent's two diagonals
        diag_s = abs((nx + ny) - opp_s)
        diag_d = abs((nx - ny) - opp_d)
        diag_break = diag_s if diag_s < diag_d else diag_d  # larger is better
        # also discourage moves that reduce Chebyshev distance too aggressively
        cur_cd = max(abs(sx - ox), abs(sy - oy))
        new_cd = max(abs(nx - ox), abs(ny - oy))
        cd_change = new_cd - cur_cd

        # lower is better: emphasize resource first, then diagonal break, then avoid closing too fast
        key = (rd, -diag_break, cd_change, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]