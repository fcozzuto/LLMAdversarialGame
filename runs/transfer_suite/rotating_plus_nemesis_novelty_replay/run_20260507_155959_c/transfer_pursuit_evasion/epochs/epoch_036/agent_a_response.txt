def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")
    my_is_pursuer = is_pursuer
    opp_is_pursuer = not my_is_pursuer

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        return (nx, ny) if valid(nx, ny) else (x, y)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_move_for(role_pursuer, px, py, ex, ey):
        best = None
        bestv = None
        for dx, dy in cand:
            nx, ny = step(px, py, dx, dy)
            d = dist((nx, ny), (ex, ey))
            if role_pursuer:
                v = -d * 10
                # small deterministic tie-break: move toward opponent roughly
                v += -(abs(nx - ex) + abs(ny - ey))
            else:
                far_corner = max(corners, key=lambda c: abs(c[0] - ex) + abs(c[1] - ey))
                v = d * 10 + (abs(far_corner[0] - nx) + abs(far_corner[1] - ny))
            if bestv is None or v > bestv:
                bestv, best = v, [dx, dy]
        return best

    my_moves = []
    for dx, dy in cand:
        nx, ny = step(sx, sy, dx, dy)
        my_moves.append((dx, dy, nx, ny))

    best_move = None
    best_val = None
    for dx, dy, nx, ny in my_moves:
        # two-ply: opponent responds greedily to our new position
        opp_dx_dy = best_move_for(opp_is_pursuer, ox, oy, nx, ny)
        nox, noy = step(ox, oy, opp_dx_dy[0], opp_dx_dy[1])

        d_after = dist((nx, ny), (nox, noy))
        if my_is_pursuer:
            # maximize capture chance: minimize distance, prefer closer absolute
            v = -d_after * 100 - (abs(nx - nox) + abs(ny - noy))
        else:
            # evade: maximize distance and try to keep drifting to farthest corner from pursuer
            far_corner = max(corners, key=lambda c: abs(c[0] - nox) + abs(c[1] - noy))
            v = d_after * 100 + (abs(far_corner[0] - nx) + abs(far_corner[1] - ny))

        if best_val is None or v > best_val:
            best_val, best_move = v, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]