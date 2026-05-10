def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set()
    for x, y in obstacles:
        obst.add((x, y))

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def eval_cell(x, y):
        if (x, y) in obst:
            return -10**18
        best = -10**18
        # Pick resource where we are most ahead (opp_dist - self_dist), with tie-breaking to be deterministic.
        for rx, ry in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            ahead = od - sd
            cap = 5.0 if (x, y) == (rx, ry) else 0.0
            # Encourage capturing soon and denying if opponent is close.
            val = cap + 3.2 * ahead - 0.35 * sd - 0.02 * cheb(x, y, ox, oy)
            if val > best:
                best = val
        return best

    bestv = -10**18
    bestm = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = eval_cell(nx, ny)
        if v > bestv:
            bestv = v
            bestm = [dx, dy]
    return bestm