def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    # Scoring: pick a move that improves "race" over resources (self closer than opponent),
    # while softly pushing away from moving into opponent's immediate threat.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh): 
            continue
        if (nx, ny) in obs:
            continue

        local = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we get closer than opponent, gain strongly; otherwise penalize.
            race = (do - ds)
            val = 10.0 * race - ds
            # Prefer collecting sooner.
            if ds == 0:
                val += 1000.0
            # Small penalty for moving into opponent adjacency (resource deniers often block routes).
            if cheb(nx, ny, ox, oy) <= 1 and (rx, ry) != (nx, ny):
                val -= 3.0
            # Discount far resources a bit.
            val -= 0.2 * (ds + do)
            if val > local:
                local = val
        if local > best_score:
            best_score = local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]