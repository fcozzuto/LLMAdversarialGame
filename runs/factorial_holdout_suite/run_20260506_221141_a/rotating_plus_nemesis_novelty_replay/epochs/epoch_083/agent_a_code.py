def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def rank(cell):
        sd = cheb(sx, sy, cell[0], cell[1])
        od = cheb(ox, oy, cell[0], cell[1])
        # Favor cells we can reach sooner, but also deny opponent.
        return (od - sd, -sd, -(cell[0] + cell[1] * 0))

    target = resources[0]
    best = rank(target)
    for c in resources[1:]:
        r = rank(c)
        if r > best:
            best = r
            target = c

    tx, ty = target
    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate next step: progress to target + worsen opponent's closest distance to that target.
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Small bonus for reducing row difference (good vs sweep behavior patterns).
        row_bonus = -abs((ny - ox) if True else 0)
        val = (opp_d - self_d, -self_d, row_bonus)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move