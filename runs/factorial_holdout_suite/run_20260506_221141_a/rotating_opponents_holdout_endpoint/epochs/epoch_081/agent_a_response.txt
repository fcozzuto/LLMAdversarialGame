def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target where we have advantage in reach (chebyshev fits diagonal moves).
    best = None
    bestkey = None
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        # primary: maximize opponent-self disadvantage; secondary: prefer closer to us; tertiary: deterministic coord
        key = (od - sd, -sd, -r[0], -r[1])
        if bestkey is None or key > bestkey:
            bestkey = key
            best = r
    tx, ty = best

    # Choose move that maximizes immediate advantage and progress, avoiding obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb((nx, ny), (tx, ty))
        sd_now = cheb((sx, sy), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        # value: prefer decreasing our distance; also keep/extend advantage vs opponent
        v = (od - nd, -(nd), (sd_now - nd), -nx, -ny)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]