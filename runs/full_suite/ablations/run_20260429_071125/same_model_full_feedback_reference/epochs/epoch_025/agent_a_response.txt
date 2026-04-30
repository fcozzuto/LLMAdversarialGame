def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w - 1) / 2.0, (h - 1) / 2.0
    cx, cy = center

    # Phase shift by time: early contest, later safer routing toward remaining resources.
    t = int(observation.get("turn_index") or 0)
    contest_weight = 1.05 if (t % 6) < 3 else 0.85
    center_weight = 0.10 if len(resources) > 6 else 0.18

    best_r = resources[0]
    best_score = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Lower is better: prioritize resources where opponent is relatively farther.
        s = md - contest_weight * od
        # Mild bias toward resources closer to center to avoid corner traps.
        s += center_weight * cheb(rx, ry, cx, cy)
        if best_score is None or s < best_score:
            best_score = s
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = (0, 0)
    best_mscore = None

    # Greedy one-step toward chosen target; break ties by increasing distance from opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        m_to = cheb(nx, ny, rx, ry)
        o_to = cheb(ox, oy, nx, ny)
        # Prefer reducing target distance; discourage stepping near opponent.
        mscore = m_to - 0.08 * cheb(nx, ny, ox, oy) + 0.02 * o_to
        if best_mscore is None or mscore < best_mscore or (mscore == best_mscore and (dx, dy) < best_move):
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]