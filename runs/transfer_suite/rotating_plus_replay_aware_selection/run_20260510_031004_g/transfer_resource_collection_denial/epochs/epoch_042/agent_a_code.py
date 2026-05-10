def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [-1, 0, 1]
    moves = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if resources:
        best_r = None
        best_score = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h):
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we have a distance advantage; tie-break deterministically.
            adv = do - ds
            key = (adv, -ds, rx, ry)
            if best_score is None or key > best_score:
                best_score = key
                best_r = (rx, ry)
        if best_r is None:
            best_r = (int(resources[0][0]), int(resources[0][1]))

        rx, ry = best_r
        # One-step lookahead: choose move maximizing next-step advantage against opponent for that target.
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            ds2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)  # opponent move unknown; keep current for stable greedy advantage
            adv2 = do2 - ds2
            # Also prefer directly approaching (smaller ds2) and, secondarily, toward top-left for determinism.
            key = (adv2, -ds2, -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move
    return [0, 0]