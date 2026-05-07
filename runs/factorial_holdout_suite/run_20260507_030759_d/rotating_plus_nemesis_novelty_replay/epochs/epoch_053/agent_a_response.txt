def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate: maximize opponent-first disadvantage (opp_dist - self_dist),
        # then minimize self distance to the best contested resource.
        best_adv = -10**18
        best_sd = 10**9
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd  # positive means we can reach earlier (or equal)
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd

        # Small tie-break toward reducing opponent access as well
        opp_touch = min(cheb(ox, oy, tx, ty) for (tx, ty) in resources)
        val = best_adv * 1000 - best_sd - opp_touch * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]