def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # capture at same cell

    def legal_moves(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                out.append((dx, dy, nx, ny))
        if not out:
            out = [(0, 0, x, y)]
        return out

    our_moves = legal_moves(sx, sy)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_move = our_moves[0]
    best_val = 10**18
    best_d = 10**18

    for dx, dy, nx, ny in our_moves:
        if nx == ox and ny == oy:
            return [dx, dy]
        # Predict opponent evasion: choose move maximizing distance to our new position
        opp_moves = legal_moves(ox, oy)
        best_opp = opp_moves[0]
        best_opp_score = -10**18
        for odx, ody, nox, noy in opp_moves:
            # small bias to continue toward a farthest corner
            far_corner = max(corners, key=lambda c: abs(c[0] - nox) + abs(c[1] - noy))
            corner_bias = abs(far_corner[0] - nox) + abs(far_corner[1] - noy)
            s = dist((nox, noy), (nx, ny)) * 100 + corner_bias
            if s > best_opp_score:
                best_opp_score = s
                best_opp = (odx, ody, nox, noy)

        _, _, pnx, pny = best_opp
        d_after = dist((pnx, pny), (nx, ny))
        # Primary: minimize predicted distance; Secondary: minimize distance right now; Tertiary: stay/move orthogonally prefer earlier dirs
        val = d_after * 1000 + dist((ox, oy), (nx, ny))
        if val < best_val or (val == best_val and d_after < best_d):
            best_val = val
            best_d = d_after
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]