def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def free(x, y):
        return inb(x, y) and (x, y) not in oset

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    dist_corner = [(c, cheb(c[0], c[1])) for c in corners]
    if is_pursuer:
        corners_sorted = sorted(dist_corner, key=lambda t: t[1])
    else:
        corners_sorted = sorted(dist_corner, key=lambda t: -t[1])
    far_corner = corners_sorted[0][0]

    def obs_block(x, y):
        if not oset:
            return 0
        md = 999
        for px, py in oset:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not free(nx, ny):
            continue
        d = cheb(nx, ny)
        clear = obs_block(nx, ny)
        corner_bias = -(abs(nx - far_corner[0]) + abs(ny - far_corner[1]))
        # pursuer: minimize distance; avoid getting too near obstacles; slight preference for corner bias
        # evader: maximize distance; encourage staying away from obstacles; prefer moving toward far_corner
        if is_pursuer:
            score = -d * 10.0 + clear * 0.6 + corner_bias * 0.05
        else:
            score = d * 10.0 + clear * 0.6 + corner_bias * 0.12
        # tie-break deterministically: prefer not moving diagonally as first, then (0,0), then lexicographic
        tie = (abs(dx) + abs(dy) != 0, dx, dy)
        if best is None or score > best or (score == best and tie < best_tie):
            best = score
            best_tie = tie
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]