def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = 10**18
    best_corner = 10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # opponent chooses move that maximizes distance to us (evasion), constrained by obstacles/bounds
        opp_best_dist = -1
        opp_best_corner = -1
        for odx, ody in cand:
            px, py = ox + odx, oy + ody
            if not valid(px, py):
                px, py = ox, oy
            d = man(px, py, nx, ny)
            far_c = max(corners, key=lambda c: man(px, py, c[0], c[1]))
            corner_score = man(px, py, far_c[0], far_c[1])
            if d > opp_best_dist or (d == opp_best_dist and corner_score > opp_best_corner):
                opp_best_dist = d
                opp_best_corner = corner_score

        # minimize evader's best achievable distance; small tie-break: also reduce their escape-to-farthest-corner potential
        if opp_best_dist < best_val:
            best_val = opp_best_dist
            best_corner = opp_best_corner
            best_move = (dx, dy)
        elif opp_best_dist == best_val:
            if opp_best_corner < best_corner:
                best_corner = opp_best_corner
                best_move = (dx, dy)
            elif opp_best_corner == best_corner:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]