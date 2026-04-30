def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def sgn(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Choose target: nearest resource; tie-break by (x,y) then by id-like deterministic key.
    tx, ty = ox, oy
    if resources:
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Strategic balance: pursue resources, but avoid giving easy capture routes to opponent.
    best_move = (0, 0)
    best_score = -10**18
    oppd_now = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        score = 0
        if resources:
            dcur = cheb(nx, ny, tx, ty)
            score += 200 - 20 * dcur

            # Mild bonus for aligning toward the nearest resource direction.
            ax = sgn(tx - nx)
            ay = sgn(ty - ny)
            if ax == dx and ay == dy:
                score += 15
        else:
            score += 0

        # Deter opponent: if close, try to increase distance; otherwise don't overreact.
        oppd = cheb(nx, ny, ox, oy)
        if oppd_now <= 3:
            score += 30 * (oppd - oppd_now)
        else:
            # Keep some space but prefer resource progress.
            score += 5 * (oppd - oppd_now)

        # Deterministic tiebreak: prefer moves that keep (nx,ny) lexicographically smaller when equal.
        # Include move parity with turn index to avoid loops.
        t = (observation.get("turn_index", 0) or 0)
        parity = ((nx + ny + t) & 1)
        score += -parity * 0.001

        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]