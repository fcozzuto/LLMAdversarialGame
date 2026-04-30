def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    opp_adj_now = cheb(sx, sy, ox, oy) <= 1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        opp_adj = cheb(nx, ny, ox, oy) <= 1

        worst_adv = None
        best_adv = None
        best_us = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if worst_adv is None or adv < worst_adv:
                worst_adv = adv
            if best_adv is None or adv > best_adv:
                best_adv = adv
            usd = cheb(nx, ny, rx, ry)
            if best_us is None or usd < best_us:
                best_us = usd

        # Primary: maximize worst-case advantage; secondary: maximize best_adv
        # Tertiary: minimize our distance to nearest resource; then prefer avoiding opponent adjacency.
        key = (-worst_adv, -best_adv, best_us, 1 if opp_adj else 0, 0 if opp_adj_now else 1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]