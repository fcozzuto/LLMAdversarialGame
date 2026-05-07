def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)
    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Pick a resource where we are likely to collect first; if none, pick best “close race”.
    best_cell = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Strongly reward being first; also reward smaller own distance.
        score = 0
        if sd == 0:
            score += 1000
        if sd < od:
            score += 250 + (od - sd) * 20
        else:
            score -= 50 + (sd - od) * 15
        score += (od - sd) * 6
        score += -sd * 3
        # Mild prefer toward the center for stability.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -((rx - cx) ** 2 + (ry - cy) ** 2) * 0.01
        if score > best_score:
            best_score = score
            best_cell = (rx, ry)

    rx, ry = best_cell
    if sx == rx and sy == ry:
        return [0, 0]

    # Greedy step toward chosen target; break ties by staying away from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(nx, ny, ox, oy)
        # Prefer immediate progress, then separation from opponent.
        val = -nsd * 10 + nod * 0.2
        # If this move grabs the resource this turn, make it dominant.
        if nx == rx and ny == ry:
            val += 10000
        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)
    return [int(best_move[0]), int(best_move[1])]