def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Corner/edge bias: prefer moves that push toward the nearest corner of the opponent
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    def corner_score(x, y):
        dmin = None
        for cx, cy in corners:
            d = abs(cx - x) + abs(cy - y)
            if dmin is None or d < dmin:
                dmin = d
        return -dmin  # closer to a corner => higher score

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Primary: reduce distance to opponent
        dist = max(abs(ox - nx), abs(oy - ny))  # Chebyshev for diagonal chase

        # Secondary: keep opponent "boxed" by preferring relative motion toward their nearest corner
        cc = corner_score(nx, ny)
        # Tertiary: small bias toward moving in the general direction of opponent
        dirbias = (1 if (dx == 0 and ox != nx and (ox - nx) > 0) else 0)
        # Use dot product sign proxy without floating ops
        toward = 0
        if (ox - sx) * dx + (oy - sy) * dy > 0:
            toward = 1

        v = dist * 1000 - cc * 10 - toward
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]